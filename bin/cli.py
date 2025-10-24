#! /usr/bin/env python
import logging

import click

from agriphyto_schema.constants import AVAILABLE_DICOS, LOG_LEVEL
from agriphyto_schema.data.parse_dicos import parse_dico

logging.basicConfig(
    level=logging.getLevelNamesMapping()[LOG_LEVEL],
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
)


@click.group()
@click.version_option(package_name="agriphyto_schema")
def cli():
    pass


@cli.command()
@click.option(
    "--dico_name",
    "-d",
    required=True,
    help=f"Parse an Excel data dictionary to create a pandera schema for data validation. Available dicos are : 'all' or one in {list(AVAILABLE_DICOS.keys())}",
)
def parse(dico_name: str) -> None:
    """
    Parse an Excel data dictionary to create a pandera schema for data validation.
    """

    if dico_name == "all":
        for dico in AVAILABLE_DICOS:
            parse_dico(dico)
    else:
        parse_dico(dico_name)


@cli.command()
def create_dico() -> None:
    """
    Create the aggregated data dictionary CSV from all pandera schemas.
    """
    from agriphyto_schema.data.create_agriphyto_dico import aggregate_schemas

    aggregate_schemas()


if __name__ == "__main__":
    cli()
