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

    async with qtrio.enter_emissions_channel(
        signals=[widget.label.text_changed],
    ) as emissions:
        async with trio.open_nursery() as nursery:
            widget = nursery.start(qtrio.examples.buildingrespect.Widget.start, message)
            await trio.sleep(1)
            for _ in message:
                print("outer before", flush=True)
                widget.button.click()
                print("outer after", flush=True)

            with trio.move_on_after(1):
                async for emission in emissions.channel:
                    [text] = emission.args
                    results.append(text)

            widget.button.click()

            # await qtrio.examples.buildingrespect.main(
            #     widget=widget,
            #     message=message,
            # )

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
