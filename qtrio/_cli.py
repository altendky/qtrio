import click


@click.group()
def cli():
    """QTrio - a library bringing Qt GUIs together with async and await via Trio"""

    pass


@cli.group()
def examples():
    """Run code examples."""

    pass


@examples.command()
def emissions():  # pragma: no cover
    """A simple demonstration of iterating over signal emissions."""

    import qtrio.examples.emissions

    qtrio.run(qtrio.examples.emissions.main)
