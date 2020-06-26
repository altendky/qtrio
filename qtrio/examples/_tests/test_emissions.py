timeout = 10


def test_main(testdir):
    test_file = r"""
    import faulthandler

    import qtrio
    from qtpy import QtCore
    import trio
    import trio.testing

    import qtrio.examples.emissions

    @qtrio.host
    async def test_example(request, qtbot):
        faulthandler.dump_traceback_later(2.5)
        window = qtrio.examples.emissions.Window.build()
        qtbot.addWidget(window.widget)

        results = []

        async def user():
            await trio.sleep(1)
            window.widget.close()

        async with trio.open_nursery() as nursery:
            nursery.start_soon(user)

            await qtrio.examples.emissions.main(window=window)

        assert results == ["1", "2", "3", "2", "1", "0", "-1"]
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess("--capture=no", timeout=timeout)
    result.assert_outcomes(passed=1)


def test_middle(testdir):
    test_file = r"""
    import faulthandler
    from qtpy import QtWidgets

    import qtrio
    import qtrio.examples.emissions

    @qtrio.host
    async def test(request):
        faulthandler.dump_traceback_later(2.5)
        widget = qtrio.examples.emissions.QSignalsWidget()
        widget.show()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess("--capture=no", timeout=timeout)
    result.assert_outcomes(passed=1)


def test_minimal(testdir):
    test_file = r"""
    import faulthandler
    from qtpy import QtWidgets
    import qtrio

    def test(request):
        faulthandler.dump_traceback_later(2.5)
        app = QtWidgets.QApplication([])
        widget = QtWidgets.QWidget()
        widget.show()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess("--capture=no", timeout=timeout)
    result.assert_outcomes(passed=1)


def test_hosted(testdir):
    test_file = r"""
    import faulthandler
    from qtpy import QtWidgets
    import qtrio

    @qtrio.host
    async def test(request):
        faulthandler.dump_traceback_later(2.5)
        widget = QtWidgets.QWidget()
        widget.show()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess("--capture=no", timeout=timeout)
    result.assert_outcomes(passed=1)
