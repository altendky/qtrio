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
            other_button = SignaledButton()
            print('+++++', 'test_example before other_button.show()', delta())
            other_button.show()
            print('+++++', 'test_example after other_button.show()', delta())

            nursery.start_soon(user)
            print('+++++', 'test_example after nursery.start_soon()', delta())

            button.show()
            print('+++++', 'test_example after button.show()', delta())
    finally:
        print('+++++', 'test_example finally', delta())
