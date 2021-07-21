import qtrio._tests.helpers

pytest_plugins = "pytester"

qtrio_preshow_workaround_fixture = qtrio._tests.helpers.qtrio_preshow_workaround_fixture
qtrio_testdir_fixture = qtrio._tests.helpers.qtrio_testdir_fixture
qtrio_optional_hold_event_fixture = qtrio._tests.helpers.optional_hold_event_fixture
