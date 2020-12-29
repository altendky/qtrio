import pathlib
import random
import sys
import typing

import hyperlink
import pytest
try:
    import quart_trio
except ImportError:
    quart_trio = None
import trio

import qtrio.dialogs
import qtrio.examples.download


pytestmark = pytest.mark.skipif(
    quart_trio is None, reason="quart-trio is not available"
)


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


async def test_get_dialog(
    chunked_data: typing.List[bytes],
    http_application: quart_trio.QuartTrio,
    url: hyperlink.URL,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    url = hyperlink.URL.from_text("http://test/")
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

        # TODO: humm, have to emit the canceled signal not call .cancel() to simulate
        #       the button click since we don't manage yet to find the button to
        #       .click() it.  Emitting .canceled triggers .cancel but not the other way
        #       around (at least when the content length is known for some reason...).
        progress_dialog.dialog.canceled.emit()

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
