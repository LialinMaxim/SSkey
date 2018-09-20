import json

import simplexml

from flask import make_response
from flask_restplus import Api


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


def output_xml(data, code, headers=None):
    """Outputs data in XML format

    :param data: output data
    :param code: HTTP code
    :param headers: None or XML format
    :return: response
    """
    response = make_response(simplexml.dumps({'response': data}), code)
    response.headers.extend(headers or {})
    return response


class RepresentationApi(Api):
    """Redefinition of the Api class

    Can be extended for other representation formats (e.g. xml, html, csv).
    """

    def __init__(self, *args, **kwargs):
        super(RepresentationApi, self).__init__(*args, **kwargs)
        self.representations = {
            'application/json': output_json,
            'application/xml': output_xml,
        }
