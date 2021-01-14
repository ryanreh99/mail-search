import json

from django.http import HttpResponse


def json_response(res_type: str,
                  data: dict,
                  status: int) -> HttpResponse:
    content = {"result": res_type}
    content.update(data)

    return HttpResponse(
        content=json.dumps(
            content,
        ),
        content_type='application/json',
        status=status,
    )


def json_success(data: dict={}) -> HttpResponse:
    return json_response(
        res_type="success",
        data=data,
        status=200,
    )


def json_error(data: dict={}) -> HttpResponse:
    return json_response(
        res_type="error",
        data=data,
        status=400,
    )