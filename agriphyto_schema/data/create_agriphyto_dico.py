"""
Aggregate pandera data schemas into one data table to be used in the streamlit GUI application.
"""

import logging

import pandas as pd
import pandera as pa

from agriphyto_schema.constants import (
    AGRIPHYTO_DICO_NAME,
    COLNAME_OUT_DB,
    COLNAME_OUT_LIBELLE,
    COLNAME_OUT_NOMENCLATURE,
    COLNAME_OUT_PANDERA_TYPE,
    COLNAME_OUT_TABLE,
    COLNAME_OUT_VARIABLE,
    DIR2DATA,
    DIR2SCHEMA,
)
from agriphyto_schema.utils import pandera_from_json

logger = logging.getLogger(__name__)


def pandera_schema2df(schema: pa.DataFrameSchema, db_name: str, table_name: str) -> pd.DataFrame:
    """
    Convert a pandera DataFrameSchema into a pandas DataFrame representing the data dictionary.
    Parameters
    ----------
    schema : pa.DataFrameSchema
        The pandera DataFrameSchema to convert.
    db_name : str
        The name of the database.
    table_name : str
        The name of the table.
    Returns
    """
    table_dico = []
    for colname, col_schema in schema.columns.items():
        nomenclature = col_schema.metadata.get("nomenclature", None) if col_schema.metadata else None
        col_line = {
            COLNAME_OUT_DB: db_name,
            COLNAME_OUT_TABLE: table_name,
            COLNAME_OUT_VARIABLE: colname,
            COLNAME_OUT_LIBELLE: col_schema.title,
            COLNAME_OUT_PANDERA_TYPE: str(col_schema.dtype.type.name),
            COLNAME_OUT_NOMENCLATURE: nomenclature,
        }
        table_dico.append(col_line)
    return pd.DataFrame(table_dico)


def aggregate_schemas() -> pd.DataFrame:
    """
    Aggregate multiple pandera schemas into one dictionary (pandas dataframe).
    By default, aggregates all available schemas in DIR2SCHEMA.

    Returns
    -------
    pd.DataFrame
        Aggregated data dictionary as a pandas DataFrame.
    """

    available_schemas = list(DIR2SCHEMA.iterdir())
    aggregated_schemas_list = []
    for schema_path in available_schemas:
        schema_name = schema_path.stem
        db_name, table_name = schema_name.split("__", 1)
        schema_path = DIR2SCHEMA / f"{schema_name}.json"
        schema = pandera_from_json(schema_path)
        pd_dico = pandera_schema2df(schema, db_name, table_name)
        aggregated_schemas_list.append(pd_dico)

    full_dico = pd.concat(aggregated_schemas_list, axis=0, ignore_index=True)
    path2dico = DIR2DATA / f"{AGRIPHYTO_DICO_NAME}.csv"
    full_dico.to_csv(DIR2DATA / "agriphyto_data_dictionary.csv", index=False)
    logger.info(f"Aggregated data dictionary saved to {path2dico}")
    return full_dico
