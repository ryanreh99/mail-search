from django.urls import path

from server.views.auth import oauth2callback
from server.views.api import (
    fetch_users,
    fetch_subject,
    fetch_datetime,
    display_messages,
    update_messages,
)
from server.views.home import (
    upload,
    home,
    reset,
    signin,
)

urlpatterns = [
    path('home', home, name='home'),
    path('upload', upload, name='upload'),
    path('reset', reset, name='reset'),
    path('signin', signin, name='signin'),
    path('accounts/google/', oauth2callback, name='oauth2callback'),
    path('messages/user/', fetch_users, name='fetch-users'),
    path('messages/subject/', fetch_subject, name='fetch-subject'),
    path('messages/datetime/', fetch_datetime, name='fetch-datetime'),
    path('messages/view/', display_messages, name='display-messages'),
    path('messages/action/', update_messages, name='update-messages'),
]