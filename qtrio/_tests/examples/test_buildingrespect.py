import typing

import pytestqt.qtbot
import trio
import trio.testing

import qtrio
import qtrio.examples.buildingrespect


async def test_main(qtbot: pytestqt.qtbot.QtBot) -> None:
    message = "test world"

    async with trio.open_nursery() as nursery:
        widget: qtrio.examples.buildingrespect.Widget = await nursery.start(
            qtrio.examples.buildingrespect.Widget.start, message
        )
        qtbot.addWidget(widget.widget)

        async with qtrio.enter_emissions_channel(
            signals=[widget.text_changed],
        ) as emissions:
            # lazily click the button and collect results in the memory channel rather
            # than starting concurrent tasks.

            # close the send channel so the receive channel knows when it is done
            async with emissions.send_channel:
                for _ in message:
                    widget.button.click()

                # give Qt etc a chance to handle the clicks before closing the channel
                await trio.testing.wait_all_tasks_blocked()

            results: typing.List[typing.Tuple[object]] = [
                emission.args async for emission in emissions.channel
            ]

            widget.button.click()

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
