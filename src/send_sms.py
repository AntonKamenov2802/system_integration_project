
from user_information import name, last_name, api_key, mobile

import requests


def send_sms_code(code):
    url = 'https://fatsms.com/send-sms'
    message = f"Hi {name} {last_name}, your code is {code}"
    send_mess = {'to_phone': mobile, 'message': message, 'api_key': api_key}
    res = requests.post(url, send_mess)

    if res.status_code == 200:
        return True

    return False
