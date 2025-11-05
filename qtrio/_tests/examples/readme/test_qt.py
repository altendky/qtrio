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

    with qtbot.waitExposed(input_dialog, timeout=500):
        main_object.setup()

    [line_edit] = input_dialog.findChildren(QtWidgets.QLineEdit)
    line_edit.setText(text_to_enter)

    with qtbot.waitExposed(output_dialog, timeout=500):
        input_dialog.accept()

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

    with qtbot.waitExposed(input_dialog, timeout=500):
        main_object.setup()

    [line_edit] = input_dialog.findChildren(QtWidgets.QLineEdit)
    line_edit.setText(text_to_enter)
    input_dialog.reject()

    # qtbot.wait(1_000)

    output_text = output_dialog.text()

    assert output_text == ""
