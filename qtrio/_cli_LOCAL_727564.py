import click


@click.group()
def cli():
    pass


@cli.group()
def examples():
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
def download(url, destination, fps):
    import qtrio.examples.download

    qtrio.run(qtrio.examples.download.main, url, destination, fps)
