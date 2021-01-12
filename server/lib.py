import base64

from django.conf import settings


def get_messages(service, user_id="me"):
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
    for id in message_ids:
        msg_dict: dict = {}

        msg = message_endpoint.get(
            userId=user_id,
            id=id,
            format='full'
        ).execute()

        # UNREAD, IMPORTANT, INBOX, CATEGORY_PERSONAL
        msg_dict['labels'] = msg['labelIds']

        payload = msg['payload']
        if payload['mimeType'] != 'multipart/alternative':
            continue

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

            if key in STORE_HEADERS:
                msg_dict[key] = value

        message_part = payload['parts'][0]
        if message_part['mimeType'] != 'text/plain':
            continue

        body = message_part['body']['data']
        body = base64.b64decode(body).decode("utf-8")
        msg_dict['body'] = body

        all_msgs.append(msg_dict)
    
    return all_msgs
