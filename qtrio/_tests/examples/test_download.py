import pathlib
import random
import trio

import hyperlink
import pytest
import pytest_httpx

import qtrio.dialogs
import qtrio.examples.download


async def test_get_dialog(
    httpx_mock: pytest_httpx.HTTPXMock, tmp_path: pathlib.Path
) -> None:
    temporary_directory = trio.Path(tmp_path)

    random_generator = random.Random(0)
    url = hyperlink.URL.from_text("http://test/file")
    data = bytes(random_generator.randrange(256) for _ in range(1_000_000))
    destination = temporary_directory.joinpath("file")

    httpx_mock.add_response(
        url=url.asText(),
        method="GET",
        data=data,
        headers={"content-length": str(len(data))},
    )

    progress_dialog = qtrio.dialogs.create_progress_dialog()
    message_box = qtrio.dialogs.create_message_box()

    async def user():
        emission = await emissions.channel.receive()
        assert emission.is_from(signal=message_box.shown)

        assert message_box.accept_button is not None
        message_box.accept_button.click()

    async with trio.open_nursery() as nursery:
        async with qtrio.enter_emissions_channel(
            signals=[message_box.shown],
        ) as emissions:
            nursery.start_soon(user)

            await qtrio.examples.download.get_dialog(
                url=url,
                destination=destination,
                fps=0.1,
                progress_dialog=progress_dialog,
                message_box=message_box,
            )

    async with await destination.open("rb") as written_file:
        written = await written_file.read()

    assert written == data


async def asynchronize(sequence):
    for element in sequence:
        yield element


def randomly_chunked_bytes(
    random_generator, chunk_size_minimum, chunk_size_maximum, chunk_count
):
    return [
        bytes(
            random_generator.randrange(256)
            for _ in range(
                random_generator.randrange(chunk_size_minimum, chunk_size_maximum)
            )
        )
        for _ in range(chunk_count)
    ]


random_generator = random.Random(0)


@pytest.mark.parametrize(
    argnames=["chunked_data"],
    argvalues=[
        [
            [
                *randomly_chunked_bytes(
                    random_generator=random_generator,
                    chunk_size_minimum=10,
                    chunk_size_maximum=20,
                    chunk_count=10,
                ),
                b"",
            ]
            * 2
        ],
        [[bytes(random_generator.randrange(256) for _ in range(1_000))]],
    ],
    ids=["Many chunks", "One chunk"],
)
@pytest.mark.parametrize(
    argnames=["content_length_specified"],
    argvalues=[[False], [True]],
    ids=["Unknown content length", "Known content length"],
)
async def test_get_chunked(
    chunked_data,
    content_length_specified: bool,
    httpx_mock: pytest_httpx.HTTPXMock,
    tmp_path: pathlib.Path,
) -> None:
    temporary_directory = trio.Path(tmp_path)

    url = hyperlink.URL.from_text("http://test/file")
    data = b"".join(chunked_data)
    destination = temporary_directory.joinpath("file")

    headers = {}

    if content_length_specified:
        content_length = len(data)
        headers["content-length"] = str(len(data))
    else:
        content_length = None

    httpx_mock.add_response(
        url=url.asText(),
        method="GET",
        data=asynchronize(chunked_data),
        headers=headers,
    )

    progresses = []

    async for progress in qtrio.examples.download.get(
        url=url, destination=destination, update_period=0
    ):
        progresses.append(progress)

    async with await destination.open("rb") as written_file:
        written = await written_file.read()

    expected_downloaded_progress = [0]
    for chunk in chunked_data:
        expected_downloaded_progress.append(
            expected_downloaded_progress[-1] + len(chunk)
        )

    assert written == data
    assert [progress.total for progress in progresses] == [content_length] * (
        len(chunked_data) + 1
    )
    assert [
        progress.downloaded for progress in progresses
    ] == expected_downloaded_progress
