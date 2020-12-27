import pathlib
import random
import trio

import hyperlink
import pytest_httpx

import qtrio.dialogs
import qtrio.examples.download


async def test_get_dialog(httpx_mock: pytest_httpx.HTTPXMock, tmp_path: pathlib.Path):
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


async def test_get(httpx_mock: pytest_httpx.HTTPXMock, tmp_path: pathlib.Path):
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

    progresses = []

    async for progress in qtrio.examples.download.get(
        url=url, destination=destination, update_period=10
    ):
        progresses.append(progress)

    async with await destination.open("rb") as written_file:
        written = await written_file.read()

    assert written == data
    assert progresses[0].downloaded == 0
    assert progresses[-1].downloaded == len(data)
    assert all(progress.total == len(data) for progress in progresses)
