"""This module provides general Qt related utilities that are not Trio specific."""

import contextlib

from qtpy import QtCore

import qtrio._python


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
            signal = QtCore.Signal(*args, **kwargs)

        self.object_cls = _SignalQObject

    def __get__(self, instance, owner):
        if instance is None:
            return self

        o = self.object(instance=instance)

        return o.signal

    def object(self, instance):
        d = getattr(instance, self.attribute_name, None)

        if d is None:
            d = {}
            setattr(instance, self.attribute_name, d)

        o = d.get(self.object_cls)
        if o is None:
            o = self.object_cls()
            d[self.object_cls] = o

        return o


Signal.attribute_name = qtrio._python.identifier_path(Signal)


@contextlib.contextmanager
def connection(signal, slot):
    """Connect a signal and slot for the duration of the context manager.

    Args:
        signal: The signal to connect.
        slot: The callable to connect the signal to.
    """
    this_connection = signal.connect(slot)

    import qtpy

    if qtpy.PYSIDE2:
        # PySide2 presently returns a bool rather than a QMetaObject.Connection
        # https://bugreports.qt.io/browse/PYSIDE-1334
        this_connection = slot

    try:
        yield this_connection
    finally:
        if qtpy.PYSIDE2:
            expected_exception = RuntimeError
        else:
            expected_exception = TypeError

        try:
            # can we precheck and avoid the exception?
            signal.disconnect(this_connection)
        except expected_exception:
            pass
