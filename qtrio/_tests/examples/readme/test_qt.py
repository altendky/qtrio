import pytestqt.qtbot
from qts import QtWidgets

import qtrio.examples.readme.qt


def test_main(qtbot: pytestqt.qtbot.QtBot, qapp: QtWidgets.QApplication) -> None:
    input_dialog = qtrio.examples.readme.qt.create_input()
    output_dialog = qtrio.examples.readme.qt.create_output()

    qtbot.add_widget(input_dialog)
    qtbot.add_widget(output_dialog)

    text_to_enter = "everyone"

    main_object = qtrio.examples.readme.qt.Main(
        application=qapp,
        input_dialog=input_dialog,
        output_dialog=output_dialog,
    )

    main_object.setup()

    qtbot.wait_for_window_shown(input_dialog)

    [line_edit] = input_dialog.findChildren(QtWidgets.QLineEdit)
    line_edit.setText(text_to_enter)
    input_dialog.accept()

    qtbot.wait_for_window_shown(output_dialog)

    output_text = output_dialog.text()

    output_dialog.accept()

    assert text_to_enter in output_text


def test_main_cancelled(
    qtbot: pytestqt.qtbot.QtBot, qapp: QtWidgets.QApplication
) -> None:
    input_dialog = qtrio.examples.readme.qt.create_input()
    output_dialog = qtrio.examples.readme.qt.create_output()

    qtbot.add_widget(input_dialog)
    qtbot.add_widget(output_dialog)

    text_to_enter = "everyone"

    main_object = qtrio.examples.readme.qt.Main(
        application=qapp,
        input_dialog=input_dialog,
        output_dialog=output_dialog,
    )

    main_object.setup()

    qtbot.wait_for_window_shown(input_dialog)

    [line_edit] = input_dialog.findChildren(QtWidgets.QLineEdit)
    line_edit.setText(text_to_enter)
    input_dialog.reject()

    # qtbot.wait(1_000)

    output_text = output_dialog.text()

    assert output_text == ""
