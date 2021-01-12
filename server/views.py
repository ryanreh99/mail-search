from urllib.parse import urlparse, parse_qs

from . import lib

from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


def oauth2callback(request: HttpRequest) -> HttpResponse:
    URI = request.get_full_path()
    network_data = urlparse(URI)
    url_query: dict = parse_qs(network_data.query)

    if url_query.get('error', None) is not None and url_query['error'][0] == 'access_denied':
        return HttpResponse("Authentication failed due to lack of user consent.")

    if url_query.get('state', None) is None:
        # TASK 1
        return HttpResponse("Do not navigate to this URL, run the standalone script.")

    state: str = url_query['state'][0]
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRET,
        scopes=settings.SCOPES,
        state=state
    )
    flow.redirect_uri = settings.REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # TODO: Make sessions persistent
    credentials = flow.credentials
    request.session['credentials']: dict = {
        'state': state,
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    # with open('token.pickle', 'wb') as token:
    #     pickle.dump(creds, token)

    # TASK 2
    service = build('gmail', 'v1', credentials=credentials)
    all_msgs = lib.get_messages(service)
    print(all_msgs)

    # TODO: Return Authorization token.
    return HttpResponse("Authentication Successful.")
