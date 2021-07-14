import functools
import typing

import pytestqt.qtbot
import trio
import trio.testing

import qtrio
import qtrio.examples.emissions


async def test_main(
    qtbot: pytestqt.qtbot.QtBot,
    optional_hold_event: typing.Optional[trio.Event],
) -> None:
    async with trio.open_nursery() as nursery:
        start = functools.partial(
            qtrio.examples.emissions.start_widget,
            hold_event=optional_hold_event,
        )
        widget: qtrio.examples.emissions.Widget = await nursery.start(start)
        qtbot.addWidget(widget.widget)

        if optional_hold_event is not None:
            optional_hold_event.set()
        else:
            await trio.testing.wait_all_tasks_blocked(cushion=0.1)

        await widget.serving_event.wait()

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
            button.click()
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)
            results.append(widget.label.text())

        widget.widget.close()

    assert results == ["1", "2", "3", "2", "1", "0", "-1"]
