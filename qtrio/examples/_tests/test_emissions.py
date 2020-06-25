import qtrio
from qtpy import QtCore
import trio

import qtrio.examples.emissions


@qtrio.host
async def test_example(request, qtbot):
    window = qtrio.examples.emissions.Window.build()
    qtbot.addWidget(window.widget)

    results = []

    async def user(event, task_status):
        async with qtrio.wait_signal_context(window.shown):
            task_status.started()

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
            await trio.sleep(0.01)
            results.append(window.label.text())
            await trio.sleep(0.01)

        event.set()

    async with trio.open_nursery() as nursery:
        event = trio.Event()
        await nursery.start(user, event)
        nursery.start_soon(qtrio.examples.emissions.main, window)
        await event.wait()
        nursery.cancel_scope.cancel()

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
