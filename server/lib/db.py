from django.db import connection
from django.db import transaction

from ..models import UserProfile, Message, MessageConfig


def bulk_create_users(emails_set: set) -> None:
    users_to_create = [
        UserProfile(
            email=email,
            is_active=False,
        ) for email in emails_set
    ]
    UserProfile.objects.bulk_create(users_to_create, ignore_conflicts=True)


def bulk_create_messages(all_msgs: list) -> None:
    with transaction.atomic():
        for msg_dict in all_msgs:
            # django bulk_update does not support unique values.
            msg_dict['Config'] = MessageConfig.objects.create(**msg_dict['Labels'])

    
    messages_to_create = [
        Message(
            id=msg_ob['id'],
            sender=UserProfile.objects.get(email=msg_ob['From']),
            receiver=UserProfile.objects.get(email=msg_ob['To']),
            content=msg_ob['Body'],
            date_sent=msg_ob['Date'],
            config=msg_dict['Config']
        ) for msg_ob in all_msgs
    ]
    Message.objects.bulk_create(messages_to_create, ignore_conflicts=True)


def fetch_using_users(field: str, predicate: str, value: str) -> list:
    """
    Get message ids for user fields using any predicate.
    """

    sql = f'''
SELECT
    msg.id
FROM
    server_Message msg
INNER JOIN
    server_UserProfile user
ON
    msg.{field}_id = user.id
WHERE
        user.email
{predicate}
    '%{value}%'
'''
    msg_ids = []
    with connection.cursor() as cursor:
        cursor.execute(sql)
        msg_ids = [
            i[0]
            for i in cursor.fetchall()
        ]
    
    return msg_ids

def fetch_using_subject(field: str, predicate: str, value: str) -> list:
    """
    Get message ids for subject field using any predicate.
    """
    if (predicate == 'LIKE'):
        queryset = Message.objects.filter(content__contains=value)
    else: # NOT LIKE
        queryset = Message.objects.exclude(content__contains=value)

    return [obj['id'] for obj in queryset.values('id')]


def fetch_using_datetime(field: str, predicate: str, value: str) -> list:
    """
    Get message ids for datetime fields using any predicate.
    """
    if (predicate == 'lte'):
        queryset = Message.objects.filter(date_sent__lte=value)
    else: # gte
        queryset = Message.objects.filter(date_sent__gte=value)

    return [obj['id'] for obj in queryset.values('id')]
