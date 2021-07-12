import pytestqt.qtbot
from qts import QtWidgets

import qtrio.examples.readme.qt


def test_main(qtbot: pytestqt.qtbot.QtBot) -> None:
    input_dialog = qtrio.examples.readme.qt.create_input()
    output_dialog = qtrio.examples.readme.qt.create_output()

    qtbot.add_widget(input_dialog)
    qtbot.add_widget(output_dialog)

    text_to_enter = "everyone"

    main_object = qtrio.examples.readme.qt.Main(
        input_dialog=input_dialog,
        output_dialog=output_dialog,
    )

    with qtbot.wait_exposed(widget=input_dialog):
        main_object.setup()

    [line_edit] = input_dialog.findChildren(QtWidgets.QLineEdit)
    line_edit.setText(text_to_enter)

    with qtbot.wait_exposed(widget=output_dialog):
        input_dialog.accept()

    output_text = output_dialog.text()

    output_dialog.accept()

    assert text_to_enter in output_text


def test_main_cancelled(qtbot: pytestqt.qtbot.QtBot) -> None:
    input_dialog = qtrio.examples.readme.qt.create_input()
    output_dialog = qtrio.examples.readme.qt.create_output()

    qtbot.add_widget(input_dialog)
    qtbot.add_widget(output_dialog)

    text_to_enter = "everyone"

    main_object = qtrio.examples.readme.qt.Main(
        input_dialog=input_dialog,
        output_dialog=output_dialog,
    )

    with qtbot.wait_exposed(widget=input_dialog):
        main_object.setup()

    [line_edit] = input_dialog.findChildren(QtWidgets.QLineEdit)
    line_edit.setText(text_to_enter)
    input_dialog.reject()

    # qtbot.wait(1_000)

    output_text = output_dialog.text()

    assert output_text == ""
