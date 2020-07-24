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
        # await emissions.channel.receive()
        await trio.sleep(2)

        button.click()


    async with trio.open_nursery() as nursery:
        # async with qtrio.enter_emissions_channel(
        #     signals=[button.shown],
        # ) as emissions:
            button.show()
            button.hide()
            nursery.start_soon(user)

            button.show()
            return

            await qtrio.examples.buildingrespect.main(button=button)
