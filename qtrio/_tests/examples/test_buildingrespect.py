import typing

import qtrio
from qtpy import QtCore
from qtpy import QtWidgets
import trio

import qtrio.examples.buildingrespect


async def test_main(request, qtbot):
    class SignaledLabel(QtWidgets.QLabel):
        text_changed = QtCore.Signal(str)

        def setText(self, *args, **kwargs):
            super().setText(*args, **kwargs)
            self.text_changed.emit(self.text())

    widget = qtrio.examples.buildingrespect.Widget(label=SignaledLabel())
    qtbot.addWidget(widget.widget)

    message = "test world"
    results: typing.List[str] = []

    async def user():
        for _ in message:
            widget.button.click()

        with trio.move_on_after(1):
            async for emission in emissions.channel:
                [text] = emission.args
                results.append(text)

        widget.button.click()

    async with qtrio.enter_emissions_channel(
        signals=[widget.label.text_changed],
    ) as emissions:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(user)

            await qtrio.examples.buildingrespect.main(
                widget=widget,
                message=message,
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
