from qtpy import QtCore
import pytest

import qtrio._qt


def test_signal_emits(qtbot):
    """qtrio._core.Signal emits."""

    class NotQObject:
        signal = qtrio._qt.Signal()

    instance = NotQObject()

    with qtbot.wait_signal(instance.signal, 100):
        instance.signal.emit()


def test_signal_emits_value(qtbot):
    """qtrio._core.Signal emits a value."""

    class NotQObject:
        signal = qtrio._qt.Signal(int)

    result = None

    def collect_result(value):
        nonlocal result
        result = value

    instance = NotQObject()
    instance.signal.connect(collect_result)

    with qtbot.wait_signal(instance.signal, 100):
        instance.signal.emit(13)

    assert result == 13


def test_accessing_signal_on_class_results_in_our_signal():
    """qtrio._core.Signal instance accessible via class attribute."""

    class NotQObject:
        signal = qtrio._qt.Signal(int)

    assert isinstance(NotQObject.signal, qtrio._qt.Signal)


def test_our_signal_object_method_returns_qobject():
    """qtrio._core.Signal instance provides access to signal-hosting QObject."""

    class NotQObject:
        signal = qtrio._qt.Signal(int)

    instance = NotQObject()

    assert isinstance(NotQObject.signal.object(instance=instance), QtCore.QObject)


def test_connection_connects(qtbot):
    """qtrio._core.connection connects signal inside managed context."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()

    results = []

    def collect_result(value):
        results.append(value)

    instance.signal.emit(1)

    with qtrio._qt.connection(instance.signal, collect_result):
        instance.signal.emit(2)

    assert results == [2]


def test_connection_disconnects(qtbot):
    """qtrio._core.connection disconnects signal when exiting managed context."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()

    results = []

    def collect_result(value):
        results.append(value)

    with qtrio._qt.connection(instance.signal, collect_result):
        instance.signal.emit(1)

    instance.signal.emit(2)

    assert results == [1]


def test_connection_yield_can_be_disconnected(qtbot):
    """qtrio._core.connection result can be used to disconnect the signal early."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()

    results = []

    def collect_result(value):
        results.append(value)

    with qtrio._qt.connection(instance.signal, collect_result) as connection:
        instance.signal.emit(1)
        instance.signal.disconnect(connection)
        instance.signal.emit(2)

    assert results == [1]


def test_failed_connection_raises():
    """qtrio._core.connection raises TypeError on failure to connect."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal()

    instance = MyQObject()

    # TODO: get more specific about the exception
    with pytest.raises(TypeError):
        with qtrio._qt.connection(instance.signal, 2):
            pass  # pragma: no cover
