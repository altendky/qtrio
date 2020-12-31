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


@pytest.fixture(
    name="optional_text_input_dialog",
    params=[False, True],
    ids=["No text input dialog", "Text input dialog"],
)
def optional_text_input_dialog_fixture(request):
    if request.param:
        return qtrio.dialogs.create_text_input_dialog()

    return None


@pytest.fixture(
    name="optional_file_dialog",
    params=[False, True],
    ids=["No file dialog", "File dialog"],
)
def optional_file_dialog_fixture(request):
    if request.param:
        return qtrio.dialogs.create_file_save_dialog()

    return None


async def test_main(
    chunked_data: typing.List[bytes],
    http_application: quart_trio.QuartTrio,
    optional_text_input_dialog: typing.Optional[qtrio.dialogs.TextInputDialog],
    optional_file_dialog: typing.Optional[qtrio.dialogs.FileDialog],
    url: hyperlink.URL,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    data = b"".join(chunked_data)
    destination = temporary_directory.joinpath("file")

    progress_dialog = qtrio.dialogs.create_progress_dialog()
    message_box = qtrio.dialogs.create_message_box()

    async def user():
        if optional_text_input_dialog is not None:
            emission = await emissions.channel.receive()
            assert emission.is_from(optional_text_input_dialog.shown)

            assert optional_text_input_dialog.line_edit is not None
            optional_text_input_dialog.line_edit.setText(url.to_text())

            assert optional_text_input_dialog.accept_button is not None
            optional_text_input_dialog.accept_button.click()

        if optional_file_dialog is not None:
            emission = await emissions.channel.receive()
            assert emission.is_from(optional_file_dialog.shown)

            assert optional_file_dialog.dialog is not None
            await optional_file_dialog.set_path(path=destination)

            assert optional_file_dialog.accept_button is not None
            optional_file_dialog.accept_button.click()

        emission = await emissions.channel.receive()
        assert emission.is_from(message_box.shown)

        assert message_box.accept_button is not None
        message_box.accept_button.click()

    signals = []

    if optional_text_input_dialog is not None:
        signals.append(optional_text_input_dialog.shown)

    if optional_file_dialog is not None:
        signals.append(optional_file_dialog.shown)

    signals.append(message_box.shown)

    async with qtrio.enter_emissions_channel(signals=signals) as emissions:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(user)

            await qtrio.examples.download.main(
                url=url if optional_text_input_dialog is None else None,
                destination=destination if optional_file_dialog is None else None,
                fps=10,
                text_input_dialog=optional_text_input_dialog,
                file_dialog=optional_file_dialog,
                progress_dialog=progress_dialog,
                message_box=message_box,
                http_application=http_application,
            )

    async with await destination.open("rb") as written_file:
        written = await written_file.read()

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

    progress_dialog = qtrio.dialogs.create_progress_dialog()
    message_box = qtrio.dialogs.create_message_box()

    async def user():
        await emissions.channel.receive()

        assert message_box.accept_button is not None
        message_box.accept_button.click()

    async with qtrio.enter_emissions_channel(
        signals=[message_box.shown],
    ) as emissions:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(user)

            await qtrio.examples.download.get_dialog(
                url=url,
                destination=destination,
                fps=0.1,
                progress_dialog=progress_dialog,
                message_box=message_box,
                http_application=http_application,
            )

    async with await destination.open("rb") as written_file:
        written = await written_file.read()

    assert written == data


async def test_get_dialog_canceled(
    chunked_data: typing.List[bytes],
    http_application: quart_trio.QuartTrio,
    url: hyperlink.URL,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    destination = temporary_directory.joinpath("file")

    progress_dialog = qtrio.dialogs.create_progress_dialog()
    message_box = qtrio.dialogs.create_message_box()

    async def user():
        await emissions.channel.receive()

        assert progress_dialog.dialog is not None
        assert progress_dialog.dialog.isVisible()
        assert message_box.dialog is None

        assert progress_dialog.cancel_button is not None
        progress_dialog.cancel_button.click()

    async with qtrio.enter_emissions_channel(
        signals=[progress_dialog.shown],
    ) as emissions:
        with pytest.raises(qtrio.UserCancelledError):
            async with trio.open_nursery() as nursery:
                nursery.start_soon(user)

                await qtrio.examples.download.get_dialog(
                    url=url,
                    destination=destination,
                    fps=0.1,
                    progress_dialog=progress_dialog,
                    message_box=message_box,
                    http_application=http_application,
                )


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
        written = await written_file.read()

    assert written == data
    assert all(progress.total == content_length for progress in progresses)
    assert [progresses[0].downloaded, progresses[-1].downloaded] == [0, len(data)]
