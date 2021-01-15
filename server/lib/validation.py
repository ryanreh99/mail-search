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


def get_POST_fields(request: HttpRequest):
    ids = request.GET.get('ids', '')
    ids_list = ids.split(',')

    view = request.GET.get('view', False)
    mark_read = request.GET.get('mark_read', False)
    mark_unread = request.GET.get('mark_unread', False)
    move = request.GET.get('move', None)

    actions_dict = {
        'view': view,
        'mark_read': mark_read,
        'mark_unread': mark_unread,
        'move': move,
    }

    return ids_list, actions_dict


def validate_actions(request: HttpRequest):
    ids_list, actions_dict = get_POST_fields(request)

    for action in ['view', 'mark_read', 'mark_unread']:
        if actions_dict[action] == True:
            return True, 'view'
    if actions_dict['move'] is not None:
        return True, {'move': actions_dict['move']}
    
    return False, json_error(get_INCORRECT_REQUEST_PARAMS('actions'))


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