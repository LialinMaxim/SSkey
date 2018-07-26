from . import sskey


@sskey.route('/')
def index():
    return '<h1>Hello, Team!</h1>'
