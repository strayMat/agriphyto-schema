#! /usr/bin/env python
import logging

import click

from agriphyto_schema.constants import LOG_LEVEL
from agriphyto_schema.parse_dicos import AVAILABLE_DICOS, parse_dico

logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
)


@click.group()
@click.version_option(package_name="agriphyto_schema")
def cli():
    pass



@cli.command()
@click.option("--dico_name", "-d", required=True, help=f"Parse an Excel data dictionary to create a pandera schema for data validation. Available dicos are {list(AVAILABLE_DICOS.keys())}")
def parse(dico_name: str) -> None:
    """
    Parse an Excel data dictionary to create a pandera schema for data validation.
    """
    parse_dico(dico_name)

if __name__ == "__main__":
    cli()
