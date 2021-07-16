import trio

import qtrio.examples.readme.qtrio_example


async def test_main():
    text_to_enter = "everyone"

    async with trio.open_nursery() as nursery:
        dialogs = await nursery.start(qtrio.examples.readme.qtrio_example.main)

        assert dialogs.input.line_edit is not None
        dialogs.input.line_edit.setText(text_to_enter)

        assert dialogs.input.accept_button is not None
        async with qtrio._core.wait_signal_context(dialogs.output.shown):
            dialogs.input.accept_button.click()

        assert dialogs.output.dialog is not None
        output_text = dialogs.output.dialog.text()

        assert dialogs.output.accept_button is not None
        dialogs.output.accept_button.click()

        assert text_to_enter in output_text


async def test_main_cancelled():
    text_to_enter = "everyone"

    def output_was_shown(*args, **kwargs):
        assert False, "Output dialog was shown"  # pragma: no cover

    async with trio.open_nursery() as nursery:
        dialogs = await nursery.start(async_fn=qtrio.examples.readme.qtrio_example.main)

        async with qtrio.open_emissions_nursery() as emissions_nursery:
            emissions_nursery.connect_sync(
                signal=dialogs.output.shown,
                slot=output_was_shown,
            )
            assert dialogs.output.dialog is None

            assert dialogs.input.line_edit is not None
            dialogs.input.line_edit.setText(text_to_enter)

            assert dialogs.input.reject_button is not None
            dialogs.input.reject_button.click()
