from django.db import connection
from django.http import HttpRequest, HttpResponse

from server.lib.response import json_success


def fetch_users(request: HttpRequest) -> HttpResponse:
    sql = '''
SELECT DISTINCT
    user.email
FROM
    server_UserProfile user
'''
    emails = []
    with connection.cursor() as cursor:
        cursor.execute(sql)
        emails = [
            i[0]
            for i in cursor.fetchall()
        ]
    
    return json_success({'users': emails})