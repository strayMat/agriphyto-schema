"""

Parse an Excel data dictionary to create a pandera schema for data validation.

Return a pandera schema JSON file for each table defined in the data dictionary.
A schema is named after : the data dictionary name (e.g. RA2020) and the table name.
It is saved in agriphyto_schema/schemas/
"""

from logging import getLogger

import pandas as pd
import pandera as pa

from agriphyto_schema.constants import (
        AVAILABLE_DICOS,
        COLNAME_LIBELLE,
        COLNAME_PANDERA_TYPE,
        COLNAME_TABLE,
        COLNAME_TYPE,
        COLNAME_VARIABLE,
        DIR2DICO,
        DIR2SCHEMA,
        MAP_TYPES,
)

logger = getLogger(__name__)
logger.setLevel("DEBUG")



def map_type(x):
        """
        Map Excel type to Pandera type using MAP_TYPES dictionary."""
        for k, v in MAP_TYPES.items():
            if isinstance(x, str) and k.lower() in x.lower():
                return v
        return "string"

def parse_dico(dico_name: str) -> None:
    """
    Parse an Excel data dictionary to create a pandera schema for data validation.

    Parameters
    ----------
    dico_name : str
        The name of the data dictionary (e.g. "RA2020").

    Returns
    -------
    None
        Saves the pandera schema JSON files in agriphyto_schema/data/schemas/
    """
    if dico_name not in AVAILABLE_DICOS:
        available_dico = list(AVAILABLE_DICOS.keys())
        raise ValueError(f"Accepted dico_name: {available_dico}. Got {dico_name}")  # noqa: TRY003
    filepath2dico = AVAILABLE_DICOS[dico_name]["filename"]
    sheet_name_variables = AVAILABLE_DICOS[dico_name]["variable_sheet"]
    skiprows = AVAILABLE_DICOS[dico_name]["skiprows"]
    cols_to_use = AVAILABLE_DICOS[dico_name]["cols_to_use"]

    dico = pd.read_excel(
        DIR2DICO / filepath2dico,
        sheet_name=sheet_name_variables,
        skiprows=skiprows,
    )
    dico.rename(columns=cols_to_use, inplace=True)
    dico = dico[cols_to_use.values()]
    dico = dico.dropna(subset=[COLNAME_VARIABLE]).reset_index(drop=True)
    # Drop empty rows
    table_names = dico[COLNAME_TABLE].dropna().unique().tolist()
    logger.info(f"Found tables: {table_names}")
    # TODO: add modalities
    # --- nomenclature / modalities
    # mods = pd.read_excel(filepath2dico, sheet_name="2_MODALITES_Variables")
    # assuming it has at least columns: VARIABLE, MODALITE (adjust names if different)
    # mods.columns = [c.upper() for c in mods.columns]

    dico[COLNAME_PANDERA_TYPE] = dico[COLNAME_TYPE].apply(map_type)
    for table in table_names:
        n_vars = dico[dico[COLNAME_TABLE] == table].shape[0]
        logger.info(f"Table {table} has {n_vars} variables")
        table_dico = dico[dico[COLNAME_TABLE] == table].reset_index(drop=True)
        # Assemble pandera schema with categories when available
        pandera_schema = pa.DataFrameSchema(
            columns={},
            strict=True,
            coerce=True,
            name=f"{dico_name}_{table}",
            description=f"Schema for table {table} from data dictionary {dico_name}",
        )
        # Add columns
        for _, row in table_dico.iterrows():
            var_name = row.get(COLNAME_VARIABLE)
            col_schema = pa.Column(
                name=var_name,
                dtype=row.get(COLNAME_PANDERA_TYPE),
                nullable=True,
                title=row.get(COLNAME_LIBELLE),
            )
            pandera_schema.columns[var_name] = col_schema
            # if row.VARIABLE in categories:
            #     col_schema["checks"] = {
            #         "isin": categories[row.VARIABLE]  # Pandera supports Check.isin([...])
            #     }

            # Build allowed categories dict from modalities
            # categories = (
            #     mods.groupby("VARIABLE")["MODALITE"]
            #     .apply(lambda s: sorted(set(s.dropna().astype(str))))
            #     .to_dict()
            # )
        # Save to JSON
        with open(
            DIR2SCHEMA / f"{pandera_schema.name}.json",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(
                pandera_schema.to_json(indent=4, ensure_ascii=False)
            )
        logger.info(f"Saved schema for table {table} to {DIR2SCHEMA / f'{pandera_schema.name}.json'}")
