import typing

import qtrio
from qtpy import QtCore
from qtpy import QtWidgets
import trio

import qtrio.examples.crossingpaths


async def test_main(qtbot):
    class SignaledLabel(QtWidgets.QLabel):
        text_changed = QtCore.Signal(str)

        def setText(self, *args, **kwargs):
            super().setText(*args, **kwargs)
            self.text_changed.emit(self.text())

    label = SignaledLabel()
    qtbot.addWidget(label)

    results: typing.List[str] = []

    async def user():
        async for emission in emissions.channel:
            [text] = emission.args
            results.append(text)

    async with trio.open_nursery() as nursery:
        async with qtrio.enter_emissions_channel(
            signals=[label.text_changed],
        ) as emissions:
            nursery.start_soon(user)

            await qtrio.examples.crossingpaths.main(
                label=label,
                message="test world",
                change_delay=0.01,
                close_delay=0.01,
            )

    assert results == [
        "test world",
        "",
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
