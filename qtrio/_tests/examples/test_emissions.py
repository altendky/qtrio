import typing

import qtrio
from qtpy import QtCore
import trio
import trio.testing

import qtrio.examples.emissions


async def test_main(qtbot):
    window = qtrio.examples.emissions.Window.build()
    qtbot.addWidget(window.widget)

    results: typing.List[str] = []

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
            # TODO: Doesn't work reliably on macOS in GitHub Actions.  Seems to
            #       sometimes just miss the click entirely.
            # qtbot.mouseClick(button, QtCore.Qt.LeftButton)
            button.click()
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)
            results.append(window.label.text())

        window.widget.close()

    async with trio.open_nursery() as nursery:
        async with qtrio.enter_emissions_channel(
            signals=[window.widget.shown],
        ) as emissions:
            nursery.start_soon(user)

            await qtrio.examples.emissions.main(window=window)

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
