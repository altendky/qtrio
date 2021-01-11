import io
import typing

import qtrio.examples.readme.console


def test_normal_usage():
    input_file = io.StringIO("Ms. Console\n")
    output_file = io.StringIO()

    qtrio.examples.readme.console.main(input_file=input_file, output_file=output_file)

    assert (
        output_file.getvalue()
        == "What is your name? Hi Ms. Console, welcome to the team!\n"
    )


class CancellingStringIO(io.StringIO):
    def readline(  # type: ignore[override]
        self,
        size: typing.Optional[int] = -1,
    ) -> str:
        raise KeyboardInterrupt()


def test_cancellation():
    input_file = CancellingStringIO()
    output_file = io.StringIO()

    qtrio.examples.readme.console.main(input_file=input_file, output_file=output_file)

    assert output_file.getvalue() == "What is your name? "
