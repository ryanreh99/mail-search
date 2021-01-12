import os
import webbrowser

import django
from django.conf import settings

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
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission.
        access_type='offline',
        # TODO: https://developers.google.com/identity/protocols/oauth2/openid-connect#python_1
        state=None,
        # allow user to select an account amongst the multiple accounts they may have current sessions for.
        prompt='select_account',
        # Enable incremental authorizations.
        # TODO: https://developers.google.com/identity/protocols/oauth2/web-server#exchange-authorization-code
        include_granted_scopes='true',
    )

    print(f"Opening URL: {authorization_url} in new tab.")
    webbrowser.open(authorization_url)

if __name__ == '__main__':
    django.setup()
    main()