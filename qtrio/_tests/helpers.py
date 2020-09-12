import pytest
from qtpy import QtWidgets


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
