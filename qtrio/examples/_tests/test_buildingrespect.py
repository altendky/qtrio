import time

import qtrio
from qtpy import QtCore
from qtpy import QtWidgets
import trio
import trio.testing

import qtrio.examples.buildingrespect


class SignaledButton(QtWidgets.QPushButton):
    shown = QtCore.Signal()

    def showEvent(self, event):
        super().showEvent(event)
        if event.isAccepted():
            self.shown.emit()


clock = time.monotonic


def test_show(qtbot):
    start = clock()

    def delta():
        return f'{clock() - start:0.3f}'

    print('+++++', 'test_show about to create the button', delta())
    button = QtWidgets.QPushButton()
    print('+++++', 'test_show before button.show()', delta())
    button.show()
    print('+++++', 'test_show after button.show()', delta())


@qtrio.host
async def test_example(request, qtbot):
    button = SignaledButton()
    qtbot.addWidget(button)

    start = clock()

    def delta():
        return f'{clock() - start:0.3f}'

    async def user():
        print('+++++', 'test_example user() before sleep', delta())
        await trio.sleep(0)
        print('+++++', 'test_example user() after sleep', delta())

    print('+++++', 'test_example before nursery', delta())
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(user)
            print('+++++', 'test_example after nursery.start_soon()', delta())

            button.show()
            print('+++++', 'test_example after button.show()', delta())
    finally:
        print('+++++', 'test_example finally', delta())
