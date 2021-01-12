from django.urls import path

from . import views

urlpatterns = [
    path('google/', views.oauth2callback, name='oauth2callback'),
]