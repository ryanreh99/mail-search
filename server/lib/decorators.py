from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session

from server.lib.response import json_error
from server.models import UserSession


def authenticated_rest_endpoint(function):
    @csrf_exempt
    def wrap(request, *args, **kwargs):
        token = UserSession.objects.get(pk=0).token
        try:
            auth_type, access_token = request.META['HTTP_AUTHORIZATION'].split(' ')
        except Exception:
            return json_error({'data': "OAuth Access Token is required. Set correct headers."})

        if auth_type == 'Bearer' and access_token == token:
            return function(request, *args, **kwargs)
        else:
            return json_error({'data': "Invalid OAuth Access Token."})

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap