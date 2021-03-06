from sanic.exceptions import SanicException


class ValidationError(SanicException):
    status_code = 422


class NotFoundError(SanicException):
    status_code = 404
