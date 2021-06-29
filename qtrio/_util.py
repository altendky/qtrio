import typing

import qts
from qts import QtCore


SignalInstance: typing.Any
if qts.is_pyqt_5_wrapper and not hasattr(QtCore, "SignalInstance"):
    SignalInstance = QtCore.pyqtBoundSignal
else:
    SignalInstance = QtCore.SignalInstance


T = typing.TypeVar("T")


class ProtocolChecker(typing.Generic[T]):
    """Instances of this class can be used as decorators that will result in type hint
    checks to verifying that other classes implement a given protocol.  Generally you
    would create a single instance where you define each protocol and then use that
    instance as the decorator.  Note that this usage is, at least in part, due to
    Python not supporting type parameter specification in the ``@`` decorator
    expression.

    .. code-block:: python

       import typing


       class MyProtocol(typing.Protocol):
           def a_method(self): ...

       check_my_protocol = qtrio._util.ProtocolChecker[MyProtocol]()

       @check_my_protocol
       class AClass:
           def a_method(self):
               return 42092
    """

    def __call__(self, cls: typing.Type[T]) -> typing.Type[T]:
        return cls
