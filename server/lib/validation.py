from datetime import datetime

from django.http import HttpRequest, HttpResponse

from server.lib.response import json_error


INCORRECT_REQUEST_METHOD_ERROR = {'data': 'ONLY GET REQUESTS ALLOWED'}

def get_INCORRECT_REQUEST_PARAMS(key):
    return {'data': f'Key: {key} is incorrect'}


def get_fields(request: HttpRequest):
    field = request.GET.get('field', '')
    predicate = request.GET.get('predicate', 'contains')
    value = request.GET.get('value', '')

    return field, predicate, value


def validate_string_fields(request: HttpRequest, users=True):
    field, predicate, value = get_fields(request)

    if users:
        if field == 'From':
            field = 'sender'
        elif field == 'To':
            field = 'receiver'
        else:
            return False, json_error(get_INCORRECT_REQUEST_PARAMS('field'))
    else: # Subject
        if field != 'Subject':
            return False, json_error(get_INCORRECT_REQUEST_PARAMS('field'))

    if predicate == 'Contains':
        predicate = 'LIKE'
    elif predicate == 'Not equals':
        predicate = 'NOT LIKE'
    else:
        return False, json_error(get_INCORRECT_REQUEST_PARAMS('predicate'))
    
    return True, [field, predicate, value]


def validate_datetime_fields(request: HttpRequest):
    field, predicate, value = get_fields(request)

    try:
        value = datetime.strptime(value, "%d/%m/%Y").date()
    except Exception:
        return False, json_error(get_INCORRECT_REQUEST_PARAMS('value'))


    if field != 'Date Received':
        return False, json_error(get_INCORRECT_REQUEST_PARAMS('field'))
    
    if predicate == 'Less than':
        predicate = 'lte'
    elif predicate == 'Greater than':
        predicate = 'gte'
    else:
        return False, json_error(get_INCORRECT_REQUEST_PARAMS('predicate'))
    
    return True, [field, predicate, value]