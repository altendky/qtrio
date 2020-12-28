import typing

import qtpy
from qtpy import QtCore


SignalInstance: typing.Any
if qtpy.API in qtpy.PYQT5_API and not hasattr(QtCore, "SignalInstance"):
    SignalInstance = QtCore.pyqtBoundSignal
else:
    SignalInstance = QtCore.SignalInstance


T = typing.TypeVar("T")


class ProtocolChecker(typing.Generic[T]):
    def __call__(self, cls: typing.Type[T]) -> typing.Type[T]:
        return cls
