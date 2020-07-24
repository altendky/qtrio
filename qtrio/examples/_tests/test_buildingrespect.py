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


@qtrio.host
async def test_example(request, qtbot):
    button = SignaledButton()
    qtbot.addWidget(button)

    async def user():
        print('+++++', 'test_example user() before sleep')
        await trio.sleep(0)
        print('+++++', 'test_example user() after sleep')

        button.click()
        print('+++++', 'test_example user() after click')

    print('+++++', 'test_example before nursery')

    async with trio.open_nursery() as nursery:
        print('+++++', 'test_example inside nursery')
        button.show()
        print('+++++', 'test_example after button.show()')
        button.hide()
        print('+++++', 'test_example after button.hide()')
        nursery.start_soon(user)
        print('+++++', 'test_example after nursery.start_soon()')

        button.show()
        print('+++++', 'test_example after button.show()')
