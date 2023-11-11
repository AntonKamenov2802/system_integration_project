
import redis
import json
from esb_utils.utils import parse_message, validate_user,\
     convert_messages, Format, ContentType, convert_patch_message, response_message
from bottle import request, response, Bottle


# To eanble json objects for all routes
# @hook("after_request")
# def _():
#     response.content_type = "application/json"


esb_bus_app = Bottle()


@esb_bus_app.get('/read-messages/topic/<topic>/from/<start>/limit/<stop>/format/<format>')
def _(topic, start, stop, format):


    token = request.headers['token']

    authenticated = validate_user(token)

    if not authenticated:
        response.status = 401
        return

    r = redis.Redis(db=2)
    messages = r.lrange(topic, int(start), int(stop))

    converted_messages = convert_messages(messages, format, token)

    response.content_type = "format" # Return the format here
    return converted_messages


@esb_bus_app.post('/create-message/topic/<topic>')
def _(topic):
    token = request.headers['token']

    authenticated = validate_user(token)

    if not authenticated:
        response.status = 401  # unauthorized
        return

    format = request.headers['content-type']
    data = {}

    data = parse_message(request.body, format)

    r = redis.Redis(db=2)
    r.rpush(topic, json.dumps(data))

    response.status = 201  # Item created

    return


@esb_bus_app.route('/update-message/topic/<topic>/id/<id>', method="PATCH")
def _(topic, id):

    r = redis.Redis(db=2)
    messages = r.lrange(topic, 0, -1)
    decoded_messages = []
    patch = request.body
    token = request.headers['token']
    format = request.headers['content-type']

    for message in messages:
        decoded_messages.append(json.loads(message.decode()))

    for idx, message in enumerate(decoded_messages):
        if (message['id'] == id):
            if (token in message['access'] or message['access'][0] == '*'):

                patched_message = convert_patch_message(message, patch, format)
                r.lset(topic, idx, json.dumps(patched_message))
                return response_message([patched_message], format)
            else:
                response.status = 401
        else:
            response.status = 404

    return


@esb_bus_app.post("/delete-message/topic/<topic>/id/<id>")
def _(topic, id):
    r = redis.Redis(db=2)
    messages = r.lrange(topic, 0, -1)
    decoded_messages = []

    token = request.headers['token']

    for message in messages:
        decoded_messages.append(json.loads(message.decode()))

    for idx, message in enumerate(decoded_messages):
        if (message['id'] == id):
            if (token in message['access'] or message['access'][0] == '*'):
                r.lrem(topic, 0, json.dumps(message))
            else:
                response.status = 401

    return
