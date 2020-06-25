import qtrio
from qtpy import QtCore
import trio
import trio.testing

import qtrio.examples.emissions


@qtrio.host
async def test_example(request, qtbot):
    window = qtrio.examples.emissions.Window.build()
    qtbot.addWidget(window.widget)

    sequencer = trio.testing.Sequencer()
    results = []

    async def user():
        async with qtrio.wait_signal_context(window.shown):
            async with sequencer(0):
                pass

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

        async with sequencer(2):
            return

    async with trio.open_nursery() as nursery:
        nursery.start_soon(user)

        async with sequencer(1):
            nursery.start_soon(qtrio.examples.emissions.main, window)

        async with sequencer(3):
            nursery.cancel_scope.cancel()

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
