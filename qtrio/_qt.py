"""This module provides general Qt related utilities that are not Trio specific."""

import contextlib

from qtpy import QtCore


def identifier_path(it):
    """Generate an identifier based on an object's module and qualified name.  This can
    be useful such as for adding attributes to existing objects while minimizing odds
    of collisions and maximizing traceability of the related party.

    Args:
        it: The object to generate the identifer from.
    """
    return "__" + "_".join(it.__module__.split(".") + [it.__qualname__])


class Signal:
    """This is a (nearly) drop-in replacement for QtCore.Signal.  The useful difference
    is that it does not require inheriting from `QtCore.QObject`.  The not-quite part is
    that it will be a bit more complicated to change thread affinity of the relevant
    `QtCore.QObject`.  If you need this, maybe just inherit.

    This signal gets around the normally required inheritance by creating
    `QtCore.QObject` instances behind the scenes to host the real signals.  Just as
    `QtCore.Signal` uses the Python descriptor protocol to intercept the attribute
    access, so does this so it can 'redirect' to the signal on the other object.
    """
    attribute_name = None

    def __init__(self, *args, **kwargs):
        class _SignalQObject(QtCore.QObject):
            signal = QtCore.pyqtSignal(*args, **kwargs)

        self.object_cls = _SignalQObject

    def __get__(self, instance, owner):
        if instance is None:
            return self

        d = getattr(instance, self.attribute_name, None)

        if d is None:
            d = {}
            setattr(instance, self.attribute_name, d)

        o = d.get(self.object_cls)
        if o is None:
            o = self.object_cls()
            d[self.object_cls] = o

        signal = o.signal
        return signal

    def object(self, instance):
        return getattr(instance, self.attribute_name)[self.object_cls]


Signal.attribute_name = identifier_path(Signal)


@contextlib.contextmanager
def connection(signal, slot):
    """Connect a signal and slot for the duration of the context manager.

    Args:
        signal: The signal to connect.
        slot: The callable to connect the signal to.
    """
    this_connection = signal.connect(slot)
    try:
        yield this_connection
    finally:
        import qtpy

        if qtpy.API in qtpy.PYQT5_API:
            signal.disconnect(this_connection)
        else:
            # PySide2 presently returns a bool rather than a QMetaObject.Connection
            # https://bugreports.qt.io/browse/PYSIDE-1334
            signal.disconnect(slot)
