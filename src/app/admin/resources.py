from .. import app, api
from flask_restplus import Resource


@api.representation('/json')
class AdminTest(Resource):
    def get(self):
        return 'OK', 200  # OK