import json
from django.http import JsonResponse


class JSONResponse(object):
    @classmethod
    def new(cls, *, code: int, message: str, **kwargs):
        """ return a new Json Response """
        resp = JsonResponse({})
        resp.status_code = code
        payload = dict({
            'message': message
        })

        for (key, value) in kwargs.items():
            payload[key] = value

        resp.content = json.dumps(payload)
        return resp
