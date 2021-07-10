import os

import django
from django.conf import settings
from django.db import connection
from django.core.management.base import BaseCommand


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mail_search.settings')
if settings.DEVEL_MODE:
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

def display_db():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mail_search.settings')
    django.setup()

    sql = '''
SELECT
    server_Message.id, sender.email, receiver.email
FROM
    server_Message
INNER JOIN
    server_UserProfile sender
ON
    server_Message.sender_id = sender.id
INNER JOIN
    server_UserProfile receiver
ON
    server_Message.receiver_id = receiver.id
LIMIT
    3
'''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        print(cursor.fetchall())


def reset_db():
    # this drops all tables and rebuilds them
    os.remove('db.sqlite3')
    os.system("python manage.py migrate")

class Command(BaseCommand):

  def handle(self, *args, **options):
    django.setup()
    display_db()
    reset_db()
