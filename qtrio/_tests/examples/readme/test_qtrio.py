import pytest
import trio

import qtrio.examples.readme.qtrio


async def test_main():
    input_dialog = qtrio.examples.readme.qtrio.create_input()
    output_dialog = qtrio.examples.readme.qtrio.create_output()

    text_to_enter = "everyone"

    async def user(task_status):
        async with qtrio._core.wait_signal_context(input_dialog.shown):
            task_status.started()

        input_dialog.line_edit.setText(text_to_enter)

        async with qtrio._core.wait_signal_context(output_dialog.shown):
            input_dialog.accept_button.click()

        output_text = output_dialog.dialog.text()

        output_dialog.accept_button.click()

        assert text_to_enter in output_text

    async with trio.open_nursery() as nursery:
        await nursery.start(user)

        await qtrio.examples.readme.qtrio.main(
            input_dialog=input_dialog,
            output_dialog=output_dialog,
        )


async def test_main_cancelled():
    input_dialog = qtrio.examples.readme.qtrio.create_input()
    output_dialog = qtrio.examples.readme.qtrio.create_output()

    text_to_enter = "everyone"

    output_shown = False

    def output_was_shown():
        nonlocal output_shown
        output_shown = True

    output_dialog.shown.connect(output_was_shown)

    async def user(task_status):
        async with qtrio._core.wait_signal_context(input_dialog.shown):
            task_status.started()

        input_dialog.line_edit.setText(text_to_enter)

        input_dialog.reject_button.click()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)

        await qtrio.examples.readme.qtrio.main(
            input_dialog=input_dialog,
            output_dialog=output_dialog,
        )

    assert not output_shown