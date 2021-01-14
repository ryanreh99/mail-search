from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from server.lib.response import json_success, json_error
from server.lib.db import (
    fetch_using_users,
    fetch_using_subject,
    fetch_using_datetime
)
from server.lib.validation import (
    validate_string_fields,
    validate_datetime_fields,
    get_INCORRECT_REQUEST_PARAMS,
    INCORRECT_REQUEST_METHOD_ERROR
)


@csrf_exempt
def fetch_users(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(INCORRECT_REQUEST_METHOD_ERROR)

    result, ret = validate_string_fields(request, users=True)
    if result:
        field, predicate, value = ret
    else:
        return ret

    fetch_using_subject(field, predicate, value)
    return json_success(
        {'ids': fetch_using_users(field, predicate, value)}
    )


@csrf_exempt
def fetch_subject(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(INCORRECT_REQUEST_METHOD_ERROR)

    result, ret = validate_string_fields(request, users=False)
    if result:
        field, predicate, value = ret
    else:
        return ret

    return json_success(
        {'ids': fetch_using_subject(field, predicate, value)}
    )


@csrf_exempt
def fetch_datetime(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return json_error(INCORRECT_REQUEST_METHOD_ERROR)

    result, ret = validate_datetime_fields(request)
    if result:
        field, predicate, value = ret
    else:
        return ret

    return json_success(
        {'ids': fetch_using_datetime(field, predicate, value)}
    )