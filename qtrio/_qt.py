"""This module provides general Qt related utilities that are not Trio specific."""

import contextlib
import typing

from qtpy import QtCore

import qtrio._python
import qtrio._util


class Signal:
    """This is a (nearly) drop-in replacement for :class:`QtCore.Signal`.  The useful
    difference is that it does not require inheriting from :class:`QtCore.QObject`.  The
    not-quite part is that it will be a bit more complicated to change thread affinity
    of the relevant :class:`QtCore.QObject`.  If you need this, maybe just inherit.

    This signal gets around the normally required inheritance by creating
    :class:`QtCore.QObject` instances behind the scenes to host the real signals.  Just
    as :class:`QtCore.Signal` uses the Python descriptor protocol to intercept the
    attribute access, so does this so it can 'redirect' to the signal on the other
    object.
    """

    _attribute_name: typing.ClassVar[str] = ""

    def __init__(self, *args: object, **kwargs: object) -> None:
        class _SignalQObject(QtCore.QObject):
            signal = QtCore.Signal(*args, **kwargs)

        self.object_cls = _SignalQObject

    def __get__(self, instance: object, owner: object) -> qtrio._util.SignalInstance:
        if instance is None:
            return self

        o = self.object(instance=instance)

        return o.signal

    def object(self, instance: object) -> QtCore.QObject:
        """Get the :class:`QtCore.QObject` that hosts the real signal.  This can be
        called such as ``type(instance).signal_name.object(instance)``.  Yes this is
        non-obvious but you have to do something special to get around the
        :ref:`descriptor protocol <python:descriptors>` so you can get at this method
        instead of just having the underlying :class:`QtCore.SignalInstance`.

        Arguments:
            instance: The object on which this descriptor instance is hosted.

        Returns:
            The signal-hosting :class:`QtCore.QObject`.
        """
        d = getattr(instance, self._attribute_name, None)

        if d is None:
            d = {}
            setattr(instance, self._attribute_name, d)

        o = d.get(self.object_cls)
        if o is None:
            o = self.object_cls()
            d[self.object_cls] = o

        return o


Signal._attribute_name = qtrio._python.identifier_path(Signal)


@contextlib.contextmanager
def connection(
    signal: qtrio._util.SignalInstance, slot: typing.Callable[..., object]
) -> typing.Generator[
    typing.Union[QtCore.QMetaObject.Connection, typing.Callable[..., object]],
    None,
    None,
]:
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
        expected_exception: typing.Type[Exception]

        if qtpy.PYSIDE2:
            expected_exception = RuntimeError
        else:
            expected_exception = TypeError

        try:
            # can we precheck and avoid the exception?
            signal.disconnect(this_connection)
        except expected_exception:
            pass
