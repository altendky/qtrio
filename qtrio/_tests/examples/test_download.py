import functools
import os
import pathlib
import random
import sys
import typing

import hyperlink
import pytest
import trio

import qtrio.dialogs
import qtrio.examples.download


minimum_python_version_for_quart_trio = (3, 7)
if sys.version_info < minimum_python_version_for_quart_trio:
    minimum_python_version_string = ".".join(
        str(v) for v in minimum_python_version_for_quart_trio
    )
    python_version_string = ".".join(str(v) for v in sys.version_info)

    reason = (
        f"quart-trio is not available for Python <{minimum_python_version_string}."
        f"  Running in Python {python_version_string}."
    )

    # quart-trio is expected to not be available but this is the public interface that
    # pytest provides for skipping and also terminating the import of the test module.
    pytest.importorskip(modname="quart_trio", reason=reason)
    raise Exception("this should never run")  # pragma: no cover


# By the time we get here, we know that quart-trio is supposed to be available.
import quart_trio


T = typing.TypeVar("T")


async def asynchronize(sequence: typing.Iterable[T]) -> typing.AsyncIterable[T]:
    for element in sequence:
        yield element


def randomly_chunked_bytes(
    random_generator: random.Random,
    chunk_size_minimum: int,
    chunk_size_maximum: int,
    chunk_count: int,
) -> typing.List[bytes]:
    return [
        bytes(
            random_generator.randrange(256)
            for _ in range(
                random_generator.randrange(chunk_size_minimum, chunk_size_maximum)
            )
        )
        for _ in range(chunk_count)
    ]


# Just using a seeded random.Random as an easy way to get consistent data without
# storing it all in the repository.
random_generator = random.Random(0)
one_chunk: typing.List[bytes] = [
    bytes(random_generator.randrange(256) for _ in range(1_000))
]
many_chunks: typing.List[bytes] = [
    *randomly_chunked_bytes(
        random_generator=random_generator,
        chunk_size_minimum=10,
        chunk_size_maximum=20,
        chunk_count=10,
    ),
    b"",
] * 2


@pytest.fixture(
    name="chunked_data",
    params=[
        many_chunks,
        one_chunk,
    ],
    ids=["Many chunks", "One chunk"],
)
def chunked_data_fixture(request):
    return request.param


@pytest.fixture(
    name="content_length_specified",
    params=[False, True],
    ids=["Unknown content length", "Known content length"],
)
def content_length_specified_fixture(request):
    return request.param


@pytest.fixture(name="content_length")
def content_length_fixture(content_length_specified, chunked_data):
    content_length: typing.Optional[int]

    if content_length_specified:
        content_length = sum(len(chunk) for chunk in chunked_data)
    else:
        content_length = None

    return content_length


@pytest.fixture(name="pass_url", params=[True, False], ids=["pass URL", "enter URL"])
def pass_url_fixture(request):
    return request.param


@pytest.fixture(
    name="pass_destination",
    params=[True, False],
    ids=["pass destination", "enter destination"],
)
def pass_destination_fixture(request):
    return request.param


@pytest.fixture(name="url")
def url_fixture():
    return hyperlink.URL.from_text("http://test/")


@pytest.fixture(name="http_application")
def http_application_fixture(chunked_data, content_length_specified, content_length):
    application = quart_trio.QuartTrio(__name__)

    @application.route("/")
    async def root():
        headers = {}

        if content_length_specified:
            headers["content-length"] = content_length

        return asynchronize(chunked_data), 200, headers

    return application


async def test_main(
    chunked_data: typing.List[bytes],
    http_application: quart_trio.QuartTrio,
    url: hyperlink.URL,
    pass_url: bool,
    tmp_path: pathlib.Path,
    pass_destination: bool,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    data = b"".join(chunked_data)
    destination = temporary_directory.joinpath("file")

    async with trio.open_nursery() as nursery:
        start = functools.partial(
            qtrio.examples.download.Downloader.start,
            url=url if pass_url else None,
            destination=destination if pass_destination else None,
            fps=10,
            http_application=http_application,
        )
        widget: qtrio.examples.download.Downloader = await nursery.start(start)

        if not pass_url:
            await widget.text_input_shown_event.wait()
            assert widget.text_input_dialog is not None

            assert widget.text_input_dialog.line_edit is not None
            widget.text_input_dialog.line_edit.setText(url.to_text())

            assert widget.text_input_dialog.accept_button is not None
            widget.text_input_dialog.accept_button.click()

        if not pass_destination:
            await widget.file_dialog_shown_event.wait()
            assert widget.file_dialog is not None

            assert widget.file_dialog.dialog is not None
            await widget.file_dialog.set_path(path=destination)

            assert widget.file_dialog.accept_button is not None
            widget.file_dialog.accept_button.click()

        await widget.get_dialog_created_event.wait()
        assert widget.get_dialog is not None

        await widget.get_dialog.message_box_shown_event.wait()
        assert widget.get_dialog.message_box is not None

        assert widget.get_dialog.message_box.accept_button is not None
        widget.get_dialog.message_box.accept_button.click()

    async with await destination.open("rb") as written_file:
        written = await written_file.read()  # type: ignore[attr-defined]

    assert written == data


async def test_get_dialog(
    chunked_data: typing.List[bytes],
    http_application: quart_trio.QuartTrio,
    url: hyperlink.URL,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    data = b"".join(chunked_data)
    destination = temporary_directory.joinpath("file")

    async with trio.open_nursery() as nursery:
        start = functools.partial(
            qtrio.examples.download.GetDialog.start,
            url=url,
            destination=destination,
            fps=0.1,
            http_application=http_application,
        )
        widget: qtrio.examples.download.GetDialog = await nursery.start(start)

        await widget.message_box_shown_event.wait()
        assert widget.message_box is not None

        assert widget.message_box.accept_button is not None
        widget.message_box.accept_button.click()

    async with await destination.open("rb") as written_file:
        written = await written_file.read()  # type: ignore[attr-defined]

    assert written == data


async def test_get_dialog_canceled(
    chunked_data: typing.List[bytes],
    http_application: quart_trio.QuartTrio,
    url: hyperlink.URL,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    destination = temporary_directory.joinpath("file")

    with pytest.raises(qtrio.UserCancelledError):
        async with trio.open_nursery() as nursery:
            start = functools.partial(
                qtrio.examples.download.GetDialog.start,
                url=url,
                destination=destination,
                fps=0.1,
                http_application=http_application,
            )
            widget: qtrio.examples.download.GetDialog = await nursery.start(start)

            await widget.progress_dialog_shown_event.wait()
            assert widget.progress_dialog is not None

            assert widget.progress_dialog.dialog is not None
            assert widget.progress_dialog.dialog.isVisible()
            assert widget.message_box is None

            assert widget.progress_dialog.cancel_button is not None
            widget.progress_dialog.cancel_button.click()


async def test_get(
    chunked_data: typing.List[bytes],
    content_length: typing.Optional[int],
    http_application: quart_trio.QuartTrio,
    url: hyperlink.URL,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    data = b"".join(chunked_data)
    destination = temporary_directory.joinpath("file")

    progresses = []

    async for progress in qtrio.examples.download.get(
        url=url,
        destination=destination,
        update_period=0,
        http_application=http_application,
    ):
        progresses.append(progress)

    async with await destination.open("rb") as written_file:
        written = await written_file.read()  # type: ignore[attr-defined]

    assert written == data
    assert all(progress.total == content_length for progress in progresses)
    assert [progresses[0].downloaded, progresses[-1].downloaded] == [0, len(data)]
