import typing

import qtpy
from qtpy import QtCore


SignalInstance: typing.Any
if qtpy.API in qtpy.PYQT5_API and not hasattr(QtCore, "SignalInstance"):
    SignalInstance = QtCore.pyqtBoundSignal
else:
    SignalInstance = QtCore.SignalInstance
