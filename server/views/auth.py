from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.signals import user_logged_in

from server.lib.utils import get_all_messages
from server.models import UserSession

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


ACCESS_DENIED = "Authentication failed due to lack of user consent."
RUN_SCRIPT = "Do not navigate to this URL, run the standalone script."
SUCCESS = "Authentication Successful."
GSERVICE_ERROR = "GMAIL API RELATED ERROR: "

def get_SUCCESS(token):
    return "Authentication Successful. Your Access token is: " + token


def oauth2callback(request: HttpRequest) -> HttpResponse:
    URI = request.get_full_path()
    network_data = urlparse(URI)
    url_query: dict = parse_qs(network_data.query)

    if url_query.get('error', None) is not None and url_query['error'][0] == 'access_denied':
        return HttpResponse(ACCESS_DENIED)

    if url_query.get('state', None) is None:
        return HttpResponse(RUN_SCRIPT)

    state: str = url_query['state'][0]
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRET,
        scopes=settings.SCOPES,
        state=state
    )
    flow.redirect_uri = settings.REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

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

    service = build('gmail', 'v1', credentials=credentials)
    try:
        all_msgs = get_all_messages(service)
    except Exception as e:
        return HttpResponse(GSERVICE_ERROR + str(e))

    # To make credentials persistent
    access_token = credentials.token
    try:
        UserSession.objects.create(
            id = 0,
            token = access_token
        )
    except IntegrityError:
        UserSession.objects.filter(pk=0).update(token=access_token)

    return HttpResponse(get_SUCCESS(access_token))
