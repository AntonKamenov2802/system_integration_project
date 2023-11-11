from jwt import InvalidSignatureError, decode


def verify_token(token):
    try:
        print(token)
        verified = decode(
            jwt=token, key='secret', verify=True, algorithms="HS256")
        return verified
    except InvalidSignatureError:
        return False


def get_cpr_from_token(token):
    try:
        verified = decode(
            jwt=token, key='secret', verify=False, algorithms="HS256")
        return verified['cpr']
    except InvalidSignatureError:
        return False
