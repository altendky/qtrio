import click


@click.group()
def cli():
    pass


@cli.group()
def examples():
    pass


@examples.command()
def emissions():
    import qtrio.examples.emissions

    qtrio.run(qtrio.examples.emissions.main)
