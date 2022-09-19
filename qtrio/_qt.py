"""This module provides general Qt related utilities that are not Trio specific."""

import contextlib
import sys
import typing

import typing_extensions

if typing.TYPE_CHECKING or "sphinx_autodoc_typehints" in sys.modules:
    from qts import QtCore

import qtrio._python


class SignalProtocol(typing_extensions.Protocol):
    signal: typing.ClassVar["QtCore.Signal"]


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

    def __init__(self, *types: type, name: typing.Optional[str] = None) -> None:
        from qts import QtCore

        class _SignalQObject(QtCore.QObject):
            if name is None:
                signal = QtCore.Signal(*types)
            else:
                signal = QtCore.Signal(*types, name=name)

        self.object_cls: typing.Type[SignalProtocol] = _SignalQObject

    @typing.overload
    def __get__(self, instance: None, owner: object) -> "Signal":
        ...

    @typing.overload
    def __get__(self, instance: object, owner: object) -> "QtCore.SignalInstance":
        ...

    def __get__(
        self, instance: object, owner: object
    ) -> typing.Union["Signal", "QtCore.SignalInstance"]:
        if instance is None:
            return self

        o = self.object(instance=instance)

        return o.signal

    def object(self, instance: object) -> "QtCore.QObject":
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
        d: typing.Optional[
            typing.Dict[typing.Type[SignalProtocol], QtCore.QObject]
        ] = getattr(instance, self._attribute_name, None)

        if d is None:
            d = {}
            setattr(instance, self._attribute_name, d)

        o: typing.Optional[QtCore.QObject] = d.get(self.object_cls)
        if o is None:
            o = self.object_cls()
            d[self.object_cls] = o

        return o


Signal._attribute_name = qtrio._python.identifier_path(Signal)


@contextlib.contextmanager
def connection(
    signal: "QtCore.SignalInstance", slot: typing.Callable[..., object]
) -> typing.Generator[
    typing.Union[
        "QtCore.QMetaObject.Connection",
        typing.Callable[..., object],
        "QtCore.SignalInstance",  # TODO: https://bugreports.qt.io/browse/PYSIDE-1334
    ],
    None,
    None,
]:
    """Connect a signal and slot for the duration of the context manager.

    Args:
        signal: The signal to connect.
        slot: The callable to connect the signal to.
    """

    # if you get segfault or sigsegv here, especially from pyside2<5.15.2, make
    # sure the slot isn't on a non-hashable (frozen will make it hashable) attrs
    # class.  https://bugreports.qt.io/browse/PYSIDE-1422
    this_connection = signal.connect(slot)

    import qts

    if qts.is_pyside_5_wrapper or qts.is_pyside_6_wrapper:
        # PySide2 presently returns a bool rather than a QMetaObject.Connection
        # https://bugreports.qt.io/browse/PYSIDE-1334
        this_connection = slot

    try:
        yield this_connection
    finally:
        expected_exception: typing.Type[Exception]

        if qts.is_pyside_5_wrapper or qts.is_pyside_6_wrapper:
            expected_exception = RuntimeError
        else:
            expected_exception = TypeError

        try:
            # can we precheck and avoid the exception?
            signal.disconnect(this_connection)
        except expected_exception:
            pass
