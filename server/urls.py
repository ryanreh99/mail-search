from django.urls import path

from server.views.auth import oauth2callback
from server.views.api import fetch_users

urlpatterns = [
    path('accounts/google/', oauth2callback, name='oauth2callback'),
    path('users/', fetch_users, name='fetch-users'),
]