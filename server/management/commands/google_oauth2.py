import os
import webbrowser

import django
from django.conf import settings
from django.core.management.base import BaseCommand

import google.oauth2.credentials
from google_auth_oauthlib.flow import Flow

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mail_search.settings')
if settings.DEVEL_MODE:
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

def main():
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRET,
        scopes=settings.SCOPES)
    flow.redirect_uri = settings.REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        state=None,
        # allow user to select an account amongst the
        # multiple accounts they may have current sessions for.
        prompt='select_account',
        include_granted_scopes='true',
    )

    print(f"Opening URL: {authorization_url} in new tab.")
    webbrowser.open(authorization_url)

class Command(BaseCommand):

  def handle(self, *args, **options):
    django.setup()
    main()
