import base64
import email
from datetime import datetime

from django.conf import settings

from .models import UserProfile, Message


def build_msg_dict(msg: dict) -> dict:
    msg_dict = {}

    # UNREAD, IMPORTANT, INBOX, CATEGORY_PERSONAL
    msg_dict['Labels'] = msg['labelIds']

    payload = msg['payload']
    if payload['mimeType'] != 'multipart/alternative':
        return {}

    STORE_HEADERS = ['From', 'To', 'Date', 'Subject']
    headers = payload['headers']
    for header in headers:
        key = header['name']
        value = header['value']

        if key == 'From':
            # Obtain email id which is in the format:
            # User Name <username@gmail.com>
            if '<' in value:
                start_index: int = value.find('<') + 1
                value = value[start_index : -1]
        
        if key == 'Date':
            # Convert Date headers which is in the
            # standard RFC 2822 email headers format.
            #
            # Index 6+ unusable
            # https://docs.python.org/3/library/email.utils.html#email.utils.parsedate
            date_tuple = email.utils.parsedate(value)[:6]
            value = datetime(*date_tuple)

        if key in STORE_HEADERS:
            msg_dict[key] = value

    message_part = payload['parts'][0]
    if message_part['mimeType'] != 'text/plain':
        return {}

    # '====' is added to avoid base64 incorrect padding error
    # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
    body = message_part['body']['data'] + '===='
    body = base64.b64decode(body).decode("utf-8", 'ignore')
    msg_dict['Body'] = body

    return msg_dict

def bulk_create_users(emails_set: set) -> None:
    UserProfile.objects.bulk_create([
        UserProfile(
            email=email,
            is_active=False,
        ) for email in emails_set
    ], ignore_conflicts=True)

def bulk_create_messages(all_msgs: list) -> None:
    Message.objects.bulk_create([
        Message(
            sender=UserProfile.objects.get(email=msg_ob['From']),
            receiver=UserProfile.objects.get(email=msg_ob['To']),
            content=msg_ob['Body'],
            date_sent=msg_ob['Date'],
        ) for msg_ob in all_msgs
    ], ignore_conflicts=True)

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
        break

        user_emails.add(msg_dict['From'])
        user_emails.add(msg_dict['To'])

    bulk_create_users(user_emails)
    bulk_create_messages(all_msgs)

    return all_msgs
