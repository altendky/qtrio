import typing

import qtrio
import trio
import trio.testing

import qtrio.examples.buildingrespect


async def call(fn, count):
    for _ in range(count):
        fn()


async def test_main(qtbot):
    message = "test world"
    results: typing.List[str] = []

    async with trio.open_nursery() as nursery:
        widget = await nursery.start(
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

            async for emission in emissions.channel:
                [text] = emission.args
                results.append(text)

            widget.button.click()

    assert results == [
        "t",
        "te",
        "tes",
        "test",
        "test ",
        "test w",
        "test wo",
        "test wor",
        "test worl",
        "test world",
    ]
