
import yaml
import io
import xmltodict
import json
import redis
from dict2xml import dict2xml
from uuid import uuid4
from enum import Enum




def validate_user(token):
    r = redis.Redis(db=1)

    users = r.lrange('users', 0, -1)

    authenticated = False

    for user in users:
        user = user.decode()
        user = json.loads(user)
        if token in user.values():
            authenticated = True

    return authenticated


def convert_xml_to_json(message):
    data = xmltodict.parse(message)
    load = data['message']

    if 'access' in load:
        if not isinstance(load['access'], list):
            load['access'] = list(load['access'])

    return load


def convert_tsv_to_json(message):
    string = io.TextIOWrapper(message, encoding='utf-8').read()
    delimiter = string[4]  # take the separator
    string = string[6:]  # remove the sep= part

    lines = string.split('\n')
    headers = lines[0].split(delimiter)
    data = lines[1].split(delimiter)

    d = {}

    for key, value in zip(headers, data):
        if key == 'access':
            d[key] = value.split(',')
        else:
            d[key] = value

    return d


def convert_json_to_stream(messages):
    return json.dumps(messages)


def convert_json_to_xml(messages):
    formated_messages = []
    for message in messages:
        formated_messages.append({"message": message})
    return dict2xml(formated_messages)


def convert_json_to_yaml(messages):
    return yaml.dump(messages)


def convert_json_to_tsv(messages):
    # make a parser for the tsv
    message_tsv = ''
    return message_tsv


def convert_yaml_to_json(string):
    json_d = yaml.safe_load(string)
    return json_d


def parse_message(message, format):

    uuid = uuid4()
    data = ''

    if format == 'application/json': # those you should define in the header
        data = json.loads(message)
    if format == 'application/x-yaml':
        data = convert_yaml_to_json(message)
    if format == 'application/xml':
        ...  # parse xml, there is a function on the top of the file you can call
    if format == 'application/tsv':
        ...  # parse tsv, there is a function on the top of the file you can call

    data['id'] = str(uuid)

    return data


def convert_messages(messages, format, token):

    converted_messages = []

    for message in messages:
        message = json.load(message.decode())
        if token in message['access'] or message['access'][0] == '*':
            converted_messages.append(message)

    if format == 'json':
        return convert_json_to_stream(converted_messages)
    # if format == '...' do the same for the other messages

  


def convert_patch_message(message, patch, format):

    if format == 'application/json':
        data = json.load(message)
    if format == 'application/xml':
        data = convert_xml_to_json(message)
    # do the same for the other formats (there are methods on top)

    for key, value in data.items():
        message[key] = value

    return message


def response_message(message, format):

    if format == 'application/json':
        return convert_json_to_stream(message)
    # do the same for the other formats
