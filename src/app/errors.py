class BaseError(Exception):
    """Abstract class of custom exceptions for HTTP status codes"""
    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class InputDataError(BaseError):
    """400 Bad Request"""
    def __init__(self, reason):
        super(InputDataError, self).__init__(reason, 400)


class AuthorizationError(BaseError):
    """401 Unauthorized"""
    def __init__(self, reason):
        super(AuthorizationError, self).__init__(reason, 401)


class AccessError(BaseError):
    """403 Forbidden"""
    def __init__(self, reason):
        super(AccessError, self).__init__(reason, 403)


class SearchError(BaseError):
    """404 Not Found"""
    def __init__(self, reason):
        super(SearchError, self).__init__(reason, 404)


class ProcessingError(BaseError):
    """422 Unprocessable Entity"""
    def __init__(self, reason):
        super(ProcessingError, self).__init__(reason, 422)
