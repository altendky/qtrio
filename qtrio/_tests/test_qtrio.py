def test_importing_qtrio_does_not_import_qt(testdir):
    test_file = r"""
    import sys

    def test():
        assert 'qts' not in sys.modules, "qts should not have been imported before test"

        import qtrio

        qts_qt_modules = [
            module for module in sys.modules if module.startswith('qts.Qt')
        ]

        assert qts_qt_modules == [], "qts' Qt modules should not have been imported during test"
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess('-p', 'no:qt')
    result.assert_outcomes(passed=1)
