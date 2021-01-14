from django.urls import path

from server.views.auth import oauth2callback
from server.views.api import (
    fetch_users,
    fetch_subject,
    fetch_datetime
)


urlpatterns = [
    path('accounts/google/', oauth2callback, name='oauth2callback'),
    path('messages/user/', fetch_users, name='fetch-users'),
    path('messages/subject/', fetch_subject, name='fetch-subject'),
    path('messages/datetime/', fetch_datetime, name='fetch-datetime'),
]