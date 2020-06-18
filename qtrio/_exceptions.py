class QTrioException(Exception):
    pass


class NoOutcomesError(QTrioException):
    pass


class ReturnCodeError(QTrioException):
    pass


class UserCancelledError(QTrioException):
    pass
