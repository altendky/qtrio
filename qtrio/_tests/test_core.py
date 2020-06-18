import threading

import qtrio._core


def test_reenter_event_triggers_in_main_thread(qapp):
    result = []

    reenter = qtrio._core.Reenter()

    def post():
        event = qtrio._core.ReenterEvent(qtrio._core.REENTER_EVENT)
        event.fn = handler
        qapp.postEvent(reenter, event)

    def handler():
        result.append(threading.get_ident())

    thread = threading.Thread(target=post)
    thread.start()
    thread.join()

    qapp.processEvents()

    assert result == [threading.get_ident()]


timeout = 3


def test_run_returns_value(testdir):
    test_file = r"""
    import outcome

    import qtrio

    def test():
        async def main():
            return 29

        result = qtrio.run(main)

        assert result == qtrio.Outcomes(
            qt=outcome.Value(0),
            trio=outcome.Value(29),
        )
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_qt_quit_cancels_trio(testdir):
    test_file = r"""
    import outcome
    import PyQt5.QtCore
    import trio

    import qtrio


    def test():
        async def main():
            PyQt5.QtCore.QTimer.singleShot(
                100,
                PyQt5.QtCore.QCoreApplication.instance().lastWindowClosed.emit,
            )

            while True:
                await trio.sleep(1)

        outcomes = qtrio.run(async_fn=main)

        assert outcomes.trio.value == None
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_run_runs_in_main_thread(testdir):
    test_file = r"""
    import threading

    import qtrio


    def test():
        async def main():
            return threading.get_ident()

        outcomes = qtrio.run(main)

        assert outcomes.trio.value == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_runner_runs_in_main_thread(testdir):
    test_file = r"""
    import threading

    import qtrio


    def test():
        async def main():
            return threading.get_ident()

        runner = qtrio.Runner()
        outcomes = runner.run(main)

        assert outcomes.trio.value == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_done_callback_runs_in_main_thread(testdir):
    test_file = r"""
    import threading

    import qtrio


    def test():
        result = {}

        async def main():
            pass

        def done_callback(outcomes):
            result['thread_id'] = threading.get_ident()

        qtrio.run(async_fn=main, done_callback=done_callback)

        assert result['thread_id'] == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_done_callback_gets_outcomes(testdir):
    test_file = r"""
    import outcome

    import qtrio


    def test():
        result = {}

        async def main():
            return 93

        def done_callback(outcomes):
            result['outcomes'] = outcomes

        qtrio.run(async_fn=main, done_callback=done_callback)

        assert result['outcomes'] == qtrio.Outcomes(
            qt=None,
            trio=outcome.Value(93),
        )
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)
