from django.db import connection
from django.db import transaction
from django.db.models import F

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
        messages_to_create = [
            Message(
                id=msg_ob['id'],
                sender=UserProfile.objects.get(email=msg_ob['From']),
                receiver=UserProfile.objects.get(email=msg_ob['To']),
                content=msg_ob['Body'],
                date_sent=msg_ob['Date'],
                config=MessageConfig.objects.create(**msg_ob['Labels'])
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


def fetch_messages_using_id(ids_list: list, config=True):
    """
    Get all messages or config ids for list of message ids.
    """
    values = ['id', 'config_id']
    for label in MessageConfig.POSSIBLE_LABELS:
        values.append('config_' + label.lower())
    if not config:
        values += ['sender_id', 'receiver_id', 'content']

    queryset = Message.objects.filter(id__in=ids_list).prefetch_related(
            'config'
        ).annotate(
            config_inbox = F('config__inbox'),
            config_spam = F('config__spam'),
            config_trash = F('config__trash'),
            config_unread = F('config__unread'),
            config_starred = F('config__starred'),
            config_important = F('config__important'),
            config_sent = F('config__sent'),
            config_draft = F('config__draft'),
            config_category_personal = F('config__category_personal'),
            config_category_social = F('config__category_social'),
            config_category_promotions = F('config__category_promotions'),
            config_category_updates = F('config__category_updates'),
            config_category_forums = F('config__category_forums'),
        ).values(*values)

    query_results = []
    for data in queryset:
        row = {
            'config': {}
        }
        for key in data:
            if key[:7] == 'config_':
                row['config'][key] = data[key]
            else:
                row[key] = data[key]
        query_results.append(row)

    return query_results


def update_config_for_move(config, field):
    for label in MessageConfig.POSSIBLE_LABELS:
        if label == field:
            setattr(config, label.lower(), True)
