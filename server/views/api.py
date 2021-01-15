from django.db import connection
from django.http import HttpRequest, HttpResponse

from server.lib.response import json_success, json_error
from server.lib.db import (
    fetch_using_users,
    fetch_using_subject,
    fetch_using_datetime,
    fetch_messages_using_id,
)
from server.lib.validation import (
    validate_string_fields,
    validate_datetime_fields,
    validate_actions,
    get_INCORRECT_REQUEST_PARAMS,
    get_INCORRECT_REQUEST_METHOD_ERROR
)
from server.lib.decorators import authenticated_rest_endpoint


@authenticated_rest_endpoint
def fetch_users(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(get_INCORRECT_REQUEST_METHOD_ERROR('GET'))

    result, ret = validate_string_fields(request, users=True)
    if result:
        field, predicate, value = ret
    else:
        return ret

    fetch_using_subject(field, predicate, value)
    return json_success(
        {'ids': fetch_using_users(field, predicate, value)}
    )


@authenticated_rest_endpoint
def fetch_subject(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(get_INCORRECT_REQUEST_METHOD_ERROR('GET'))

    result, ret = validate_string_fields(request, users=False)
    if result:
        field, predicate, value = ret
    else:
        return ret

    return json_success(
        {'ids': fetch_using_subject(field, predicate, value)}
    )


@authenticated_rest_endpoint
def fetch_datetime(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(get_INCORRECT_REQUEST_METHOD_ERROR('GET'))

    result, ret = validate_datetime_fields(request)
    if result:
        field, predicate, value = ret
    else:
        return ret

    return json_success(
        {'ids': fetch_using_datetime(field, predicate, value)}
    )

@authenticated_rest_endpoint
def display_messages(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(get_INCORRECT_REQUEST_METHOD_ERROR('GET'))
    
    ids = request.GET.get('ids', '')
    ids_list = ids.split(',')

    # If True (or not passed, for normal cases) just returns the foreign key id.
    # Else when called through the script, returns other keys as well.
    config = request.GET.get('config', 'True')
    config = config == 'True' # Convert string to boolean

    return json_success(
        {'ids': fetch_messages_using_id(ids_list, config=config)}
    )


@authenticated_rest_endpoint
def update_messages(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return json_error(get_INCORRECT_REQUEST_METHOD_ERROR('POST'))

    result, action = validate_actions(request)
    if not result:
        return action
