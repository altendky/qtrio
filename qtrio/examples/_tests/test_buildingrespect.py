timeout = 10


def test_main(testdir):
    test_file = r"""
    import qtrio
    from qtpy import QtCore
    from qtpy import QtWidgets
    import trio
    import trio.testing

    import qtrio.examples.buildingrespect


    class SignaledButton(QtWidgets.QPushButton):
        shown = QtCore.Signal()

        def showEvent(self, event):
            super().showEvent(event)
            if event.isAccepted():
                self.shown.emit()


    @qtrio.host
    async def test_example(request, qtbot):
        button = SignaledButton()
        qtbot.addWidget(button)

        async def user():
            await emissions.channel.receive()

            button.click()


        async with trio.open_nursery() as nursery:
            async with qtrio.enter_emissions_channel(
                signals=[button.shown],
            ) as emissions:
                nursery.start_soon(user)

                await qtrio.examples.buildingrespect.main(button=button)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess("--capture=no", timeout=timeout)
    result.assert_outcomes(passed=1)
