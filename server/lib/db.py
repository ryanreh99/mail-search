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
