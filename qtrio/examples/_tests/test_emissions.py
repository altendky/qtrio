import qtrio
from qtpy import QtCore
from qtpy import QtWidgets
import trio
import trio.testing

import qtrio.examples.emissions


@qtrio.host(timeout=20)
async def test_main(request, qtbot):
    button = QtWidgets.QPushButton()
    button.show()
    button.hide()

    window = qtrio.examples.emissions.Window.build()
    qtbot.addWidget(window.widget)

    results = []

    async def user():
        print('+++ user() before await receive')
        await emissions.channel.receive()
        print('+++ user() after await receive')

        buttons = [
            window.increment,
            window.increment,
            window.increment,
            window.decrement,
            window.decrement,
            window.decrement,
            window.decrement,
        ]
        for button in buttons:
            print('+++ user() before mouseClick')
            qtbot.mouseClick(button, QtCore.Qt.LeftButton)
            print('+++ user() before await blocked')
            await trio.testing.wait_all_tasks_blocked(cushion=0.05)
            print('+++ user() before appending')
            results.append(window.label.text())

        window.widget.close()

    async with trio.open_nursery() as nursery:
        async with qtrio.enter_emissions_channel(
            signals=[window.widget.shown],
        ) as emissions:
            print('+++ before start_soon')
            nursery.start_soon(user)

            print('+++ before await main')
            await qtrio.examples.emissions.main(window=window)
            print('+++ after await main')

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
