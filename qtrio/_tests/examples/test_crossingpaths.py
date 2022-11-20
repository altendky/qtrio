import functools
import typing

import pytestqt.qtbot
import trio

import qtrio
import qtrio.examples.crossingpaths


async def test_main(
    qtbot: pytestqt.qtbot.QtBot, optional_hold_event: typing.Optional[trio.Event]
) -> None:
    message = "test world"

    async with trio.open_nursery() as nursery:
        start = functools.partial(
            qtrio.examples.crossingpaths.start_widget,
            message=message,
            change_delay=0.01,
            close_delay=0.01,
            hold_event=optional_hold_event,
        )
        widget: qtrio.examples.crossingpaths.Widget = await nursery.start(start)

        async with qtrio.enter_emissions_channel(
            signals=[widget.text_changed],
        ) as emissions:
            if optional_hold_event is not None:
                optional_hold_event.set()

            async with emissions.send_channel:
                await widget.done_event.wait()

            results = [emission.args async for emission in emissions.channel]

    assert results == [
        ("t",),
        ("te",),
        ("tes",),
        ("test",),
        ("test ",),
        ("test w",),
        ("test wo",),
        ("test wor",),
        ("test worl",),
        ("test world",),
    ]
