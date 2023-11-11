
import json
import jwt_verification
import send_sms
import cookie_secret
import generate_code
import redis
import email_client
import user_information
from secrets import token_urlsafe
from uuid import uuid4
from bottle import static_file, post, get, request, response, error, view, Bottle


# To eanble json objects for all routes
# @hook("after_request")
# def _():
#     response.content_type = "application/json"


login_app = Bottle()


@login_app.get('/')
@view('home')
def _():
    return static_file('home.html', root='views')


@login_app.get('/code-verification')
@view('code_check')
def _():
    return


@login_app.post('/code-verification')
def _():
    code = json.load(request.body)
    cpr = request.get_cookie('cpr', secret=cookie_secret.secret)

    r = redis.Redis(db=0)
    stored_code = r.get(cpr)

    if stored_code.decode() == code:

        r.delete(cpr)
        token = token_urlsafe(16)

        r = redis.Redis(db=1)
        uuid = uuid4()

        new_user = json.dumps({
            'id': str(uuid),
            'email': user_information.email,
            'token': token})

        r.rpush('users', new_user)
        return f'Token: {token}'
    else:
        response.status = 403
        return


@login_app.post('/validate-token')
def _():
    token = json.load(request.body)
    verified = jwt_verification.verify_token(token)

    if verified:
        code = generate_code.generate_code()

        r = redis.Redis(db=0)
        r.mset({f"{verified['cpr']}": code})

        is_send = True  # send_sms.send_sms_code(code)
        # email_client.send_email(user_information.email, code)

        if not is_send:
            response.status = 500  # internal server error
            return
    else:
        response.status = 403  # unauthorized but user is known to the server
        return

    # set a cookie with a secret
    response.set_cookie('cpr', verified['cpr'], secret=cookie_secret.secret)
    return


@login_app.get('/invalid-token')
@view('invalid_token')
def _():
    return


@login_app.error(404)
def _(error):
    print(error)
    return "Page not found"
