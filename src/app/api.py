import json

from flask import make_response
from flask_restplus import Api

from . import app


def output_json(data, code, headers=None):
    """Outputs data in JSON format

    :param data: output data
    :param code: HTTP code
    :param headers: None or JSON format
    :return: response
    """
    response = make_response(json.dumps(data), code)
    response.headers.extend(headers or {})
    return response


class RepresentationApi(Api):
    """Redefinition of the Api class

    Can be extended for other representation formats (e.g. xml, html, cvs).
    """
    def __init__(self, *args, **kwargs):
        super(RepresentationApi, self).__init__(*args, **kwargs)
        self.representations = {
            'application/json': output_json,
        }


api = RepresentationApi(app, version='0.1.1', title='SSkey', description='A simple application to safe yours passwords')
