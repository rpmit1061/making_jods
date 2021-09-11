import json

from rest_framework import renderers


class CustomResponse(renderers.BaseRenderer):
    """
    Class is used for override the response for the API.
    """
    media_type = 'application/json'
    format = 'json'

    def render(self, data, media_type=None, renderer_context=None):
        response_code = renderer_context.get('response').status_code
        custom_response = {
            'success': True if response_code in [200, 201] else False,
            'status_code': response_code,
            'data': data
        }
        return json.dumps(custom_response)
