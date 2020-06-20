from qtpy import QtCore

import qtrio._qt


def test_signal_emits(qtbot):
    class NotQObject:
        signal = qtrio._qt.Signal()

    instance = NotQObject()

    with qtbot.wait_signal(instance.signal, 100):
        instance.signal.emit()


def test_signal_emits_value(qtbot):
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
    class NotQObject:
        signal = qtrio._qt.Signal(int)

    assert isinstance(NotQObject.signal, qtrio._qt.Signal)


def test_our_signal_object_method_returns_qobject():
    class NotQObject:
        signal = qtrio._qt.Signal(int)

    instance = NotQObject()

    assert isinstance(NotQObject.signal.object(instance=instance), QtCore.QObject)


def test_connection_connects(qtbot):
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

