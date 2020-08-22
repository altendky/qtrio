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
def download(url, destination, fps):  # pragma: no cover
    import qtrio.examples.download

    qtrio.run(qtrio.examples.download.main, url, destination, fps)


@examples.command()
def emissions() -> None:  # pragma: no cover
    """A simple demonstration of iterating over signal emissions."""

    import qtrio.examples.emissions

    qtrio.run(qtrio.examples.emissions.main)
