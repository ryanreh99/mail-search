import os
import json
import requests

import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mail_search.settings')
if settings.DEVEL_MODE:
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')


def load_rules():
    with open(settings.RULES, "r") as f:
        # file closes after the execution of this block is completed.
        file_data = f.read()

    if len(file_data) == 0:
        # Loading empty file raises json.decoder.JSONDecodeError error.
        return {}
    return json.loads(file_data)

def build_message_dict(all_message_ids):
    msg_dict = {}
    for sublist in all_message_ids:
        for id in sublist:
            if id not in msg_dict:
                msg_dict[id] = 0
            msg_dict[id] += 1
    
    return msg_dict
                

def main():
    rules_file: dict = load_rules()
    BASE_URL = 'http://127.0.0.1:8000/'

    all_message_ids = []
    for rule in rules_file['rules']:
        if rule['field'] in ['From', 'To']:
            endpoint = 'messages/user/'
        elif rule['field'] == 'Subject':
            endpoint = 'messages/subject/'
        elif rule['field'] == 'Date Received':
            endpoint = 'messages/datetime/'
        
        response = requests.get(BASE_URL + endpoint, params=rule)
        response_ids = response.json()['ids']
        all_message_ids.append(response_ids)

    msg_dict = build_message_dict(all_message_ids)

    if rules_file['type'] == 'Any':
        message_ids = [id for id in msg_dict]
    else: #All
        num_rules = len(all_message_ids)
        message_ids = [
            id
            for id in msg_dict
            if msg_dict[id] == num_rules
        ]


if __name__ == '__main__':
    django.setup()
    main()