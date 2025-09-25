#! /usr/bin/env python
import logging

import click

from agriphyto_schema.constants import LOG_LEVEL
from agriphyto_schema.utils import hello

logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
)


@click.group()
@click.version_option(package_name="agriphyto_schema")
def cli():
    pass


@cli.command()
def main() -> None:
    """agriphyto_schema Main entrypoint"""
    click.secho(hello(), fg="green")


if __name__ == "__main__":
    cli()
