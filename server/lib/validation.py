from datetime import datetime

from django.http import HttpRequest, HttpResponse

from server.lib.response import json_error


def get_INCORRECT_REQUEST_METHOD_ERROR(method):
    return {'data': f'ONLY {method} REQUESTS ALLOWED'}

def get_INCORRECT_REQUEST_PARAMS(key):
    return {'data': f'Key: {key} is incorrect'}


def get_GET_fields(request: HttpRequest):
    field = request.GET.get('field', '')
    predicate = request.GET.get('predicate', 'contains')
    value = request.GET.get('value', '')

    return field, predicate, value


def validate_actions(request: HttpRequest):
    ids = request.GET.get('ids', '')
    ids_list = ids.split(',')

    mark_read = request.GET.get('mark_read', None)
    mark_unread = request.GET.get('mark_unread', None)
    move = request.GET.get('move', None)

    if mark_read is not None:
        actions_dict = {'mark_read': mark_read == 'True'}
    elif mark_unread is not None:
        actions_dict = {'mark_unread': mark_unread == 'True'}
    elif move is not None:
        actions_dict = {'move': move}
    else:
        return False, False, json_error(get_INCORRECT_REQUEST_PARAMS('actions'))

    return True, ids_list, actions_dict


def validate_string_fields(request: HttpRequest, users=True):
    field, predicate, value = get_GET_fields(request)

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
    field, predicate, value = get_GET_fields(request)

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