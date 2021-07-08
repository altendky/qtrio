import pytest
from qts import QtWidgets
import trio


@pytest.fixture(name="qtrio_preshow_workaround", scope="session", autouse=True)
def qtrio_preshow_workaround_fixture(qapp):
    dialog = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Information,
        "",
        "",
        QtWidgets.QMessageBox.Ok,
    )

    dialog.show()
    dialog.hide()


@pytest.fixture(name="qtrio_testdir", autouse=True)
def qtrio_testdir_fixture(testdir):
    text = """
    [pytest]
    trio_mode = true
    trio_run = trio
    """
    testdir.makefile(".ini", pytest=text)

    return testdir


@pytest.fixture(
    name="optional_hold_event",
    params=[lambda: None, trio.Event],
    ids=["no hold", "hold"],
)
def optional_hold_event_fixture(request):
    return request.param()
