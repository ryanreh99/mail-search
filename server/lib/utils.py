import base64
import email
import requests
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from . import db
from server.models import UserSession, Message, MessageConfig

def build_msg_dict(msg: dict) -> dict:
    msg_dict = {}
    msg_dict['id'] = msg['id']

    label_keys = [label.lower() for label in msg['labelIds']]
    label_values = [True] * len(msg['labelIds'])
    msg_dict['Labels'] = dict(zip(label_keys, label_values))

    payload = msg['payload']
    if payload['mimeType'] != 'multipart/alternative':
        return {}

    STORE_HEADERS = ['From', 'To', 'Date', 'Subject']
    headers = payload['headers']
    for header in headers:
        key = header['name']
        value = header['value']

        if key in ['From', 'To']:
            # Obtain email id which is in the format:
            # User Name <username@gmail.com>
            if '<' in value:
                start_index: int = value.find('<') + 1
                value = value[start_index : -1]
        
        elif key == 'Date':
            # Convert Date headers which is in the
            # standard RFC 2822 email headers format.
            #
            # Indexes 6+ are unusable
            # https://docs.python.org/3/library/email.utils.html#email.utils.parsedate
            date_tuple = email.utils.parsedate(value)[:6]
            value = datetime(*date_tuple, tzinfo=timezone.utc)

        if key in STORE_HEADERS:
            msg_dict[key] = value

    message_part = payload['parts'][0]
    if message_part['mimeType'] != 'text/plain':
        return {}

    # data is a base64url encoded string.
    #
    # '====' is added to avoid base64 incorrect padding error
    # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
    body = message_part['body']['data'] + '===='
    body = base64.urlsafe_b64decode(body).decode("utf-8", 'ignore')
    msg_dict['Body'] = body

    return msg_dict


def get_all_messages(service, user_id="me"):
    message_endpoint = service.users().messages()
    messages_dict: dict = message_endpoint.list(
        userId=user_id,
        maxResults=settings.MAX_RESULTS
    ).execute()
    message_ids: list = [
        msg['id']
        for msg in messages_dict.get('messages', [])
    ]

    all_msgs: list = []
    user_emails: set = set()
    for id in message_ids:
        msg = message_endpoint.get(
            userId=user_id,
            id=id,
            format='full'
        ).execute()

        msg_dict: dict = build_msg_dict(msg)
        if len(msg_dict) == 0:
            continue
        all_msgs.append(msg_dict)

        user_emails.add(msg_dict['From'])
        user_emails.add(msg_dict['To'])

    db.bulk_create_users(user_emails)
    db.bulk_create_messages(all_msgs)

    return all_msgs


def update_mail_messages(message_list, action_dict):
    request_body = {
        'addLabelIds': [],
        'removeLabelIds': []
    }

    if 'mark_read' in action_dict:
        request_body['removeLabelIds'] = 'UNREAD'
    elif 'mark_unread' in action_dict:
        request_body['addLabelIds'] = 'UNREAD'
    elif 'move' in action_dict:
        request_body['addLabelIds'] = action_dict['move']
    
    try:
        token = UserSession.objects.get(pk=0).token
    except Exception as e:
        return False

    headers = {'Authorization': 'Bearer ' + token}
    for id in message_list:
        url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{id}/modify'
        response = requests.post(url, params=request_body, headers=headers)

        if 'error' in response.json():
            print(response.json())
            return False

        message = db.fetch_messages_using_id([id])[0]
        config_id = Message.objects.get(id=id).config_id
        config = MessageConfig.objects.get(id=config_id)

        if 'mark_read' in action_dict:
            config.unread = False
        elif 'mark_unread' in action_dict:
            config.unread = True
        elif 'move' in action_dict:
            db.update_config_for_move(config, action_dict['move'])
        
        config.save()

    return True

        