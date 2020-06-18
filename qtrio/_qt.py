import contextlib

from PyQt5 import QtCore


def identifier_path(it):
    return "__" + "_".join(it.__module__.split(".") + [it.__qualname__])


class Signal:
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


class Connections:
    def __init__(self, signal, slot=None, slots=(), connect=True):
        self.signal = signal
        self.slots = slots

        if slot is not None:
            self.slots = (slot,) + self.slots

        if connect:
            self.connect()

    def connect(self):
        for slot in self.slots:
            self.signal.connect(slot)

    def disconnect(self):
        for slot in self.slots:
            self.signal.disconnect(slot)


@contextlib.contextmanager
def connection(signal, slot):
    this_connection = signal.connect(slot)
    try:
        yield this_connection
    finally:
        signal.disconnect(this_connection)
