import os
import sys
import json
import requests

import django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from server.models import UserSession

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
    try:
        token = UserSession.objects.get(pk=0).token
    except Exception as e:
        print(e)
        print("ERROR: Run `google_oauth2` script first.")
        sys.exit()
    
    # https://stackoverflow.com/questions/31282494/custom-headers-missing-in-requests-to-django
    headers = {'Authorization': 'Bearer ' + token}
    rules_file: dict = load_rules()
    BASE_URL = 'http://127.0.0.1:8000/'

    ct = 1
    print('Processing Rules....')
    all_message_ids = []
    for rule in rules_file['rules']:
        print('Rule : ' + str(ct))
        ct += 1

        if rule['field'] in ['From', 'To']:
            endpoint = 'messages/user/'
        elif rule['field'] == 'Subject':
            endpoint = 'messages/subject/'
        elif rule['field'] == 'Date Received':
            endpoint = 'messages/datetime/'
        
        response = requests.get(BASE_URL + endpoint, params=rule, headers=headers)
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
    
    ct = 1
    print('Taking Actions....')
    message_ids = ','.join(message_ids)

    from os.path import dirname, realpath, join
    ROOT_DIR: str = dirname(dirname(realpath(__file__)))
    completeName = join(ROOT_DIR, "../../msg_ids.txt")
    with open(completeName, "w") as f:
        f.write(str(message_ids))
    
    for action in rules_file['actions']:
        print('Action : ' + str(ct))
        ct += 1

        params = {'ids': message_ids}
        if list(action)[0] == 'view':
            endpoint = 'messages/view/'
            response = requests.get(BASE_URL + endpoint, params=params, headers=headers)
        else:
            params = {**params, **action}
            endpoint = 'messages/action/'
            response = requests.post(BASE_URL + endpoint, params=params, headers=headers)
        
        if response.json()['result'] == 'error':
            print('ERROR!')
            print(response.json())
            sys.exit()
    
    print("EXECUTED!")

class Command(BaseCommand):

  def handle(self, *args, **options):
    django.setup()
    main()
