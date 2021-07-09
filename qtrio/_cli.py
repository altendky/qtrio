import click


@click.group()
def cli() -> None:
    """QTrio - a library bringing Qt GUIs together with async and await via Trio"""

    pass


@cli.group()
def examples() -> None:
    """Run code examples."""

    pass


@examples.command()
def emissions() -> None:  # pragma: no cover
    """A simple demonstration of iterating over signal emissions."""

    import qtrio
    import qtrio.examples.emissions

    qtrio.run(qtrio.examples.emissions.start_widget)


@examples.command()
@click.option("--url", help="The URL to download.")
@click.option(
    "--destination",
    help="The file path to save to.",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True, allow_dash=True),
)
@click.option(
    "--fps",
    default=60,
    help="Frames per second for progress updates.",
    type=click.IntRange(min=1),
)
def download(url: str, destination: str, fps: int) -> None:  # pragma: no cover
    import qtrio
    import qtrio.examples.download

    qtrio.run(qtrio.examples.download.start_downloader, url, destination, fps)
