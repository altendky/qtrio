import functools
import typing

import pytestqt.qtbot
import trio
import trio.testing

import qtrio
import qtrio.examples.emissions


async def test_main(qtbot: pytestqt.qtbot.QtBot) -> None:
    async with trio.open_nursery() as nursery:
        hold_event = trio.Event()
        start = functools.partial(
            qtrio.examples.emissions.Widget.start,
            hold_event=hold_event,
        )
        widget: qtrio.examples.emissions.Widget = await nursery.start(start)
        qtbot.addWidget(widget.widget)

        async with qtrio.enter_emissions_channel(
            signals=[widget.widget.shown],
        ) as emissions:
            hold_event.set()

            await emissions.channel.receive()

            buttons = [
                widget.increment,
                widget.increment,
                widget.increment,
                widget.decrement,
                widget.decrement,
                widget.decrement,
                widget.decrement,
            ]

            results: typing.List[str] = []

            for button in buttons:
                # TODO: Doesn't work reliably on macOS in GitHub Actions.  Seems to
                #       sometimes just miss the click entirely.
                # qtbot.mouseClick(button, QtCore.Qt.LeftButton)
                button.click()
                await trio.testing.wait_all_tasks_blocked(cushion=0.01)
                results.append(widget.label.text())

            widget.widget.close()

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
