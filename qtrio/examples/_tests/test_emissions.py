import qtrio
from qtpy import QtCore
import trio
import trio.testing

import qtrio.examples.emissions


@qtrio.host
async def test_example(request, qtbot):
    window = qtrio.examples.emissions.Window.build()
    qtbot.addWidget(window.widget)

    results = []

    async def user():
        await emissions.channel.receive()

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
            qtbot.mouseClick(button, QtCore.Qt.LeftButton)
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)
            results.append(window.label.text())
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)

        await trio.sleep(0.2)
        window.widget.close()

    async with trio.open_nursery() as nursery:
        async with qtrio.open_emissions_channel(signals=[window.shown]) as emissions:
            async with emissions.channel:
                nursery.start_soon(user)

                await qtrio.examples.emissions.main(window=window)

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
