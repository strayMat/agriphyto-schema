"""

Parse an Excel data dictionary to create a pandera schema for data validation.

Return a pandera schema JSON file for each table defined in the data dictionary.
A schema is named after : the data dictionary name (e.g. RA2020) and the table name.
It is saved in agriphyto_schema/schemas/
"""

from logging import getLogger

import pandas as pd
import pandera.pandas as pa

from agriphyto_schema.constants import (
    AVAILABLE_DICOS,
    COLNAME_LIBELLE,
    COLNAME_PANDERA_TYPE,
    COLNAME_TABLE,
    COLNAME_TYPE,
    COLNAME_VARIABLE,
    DIR2DICO,
    DIR2NOMENCLATURES,
    DIR2SCHEMA,
    MAP_TYPES,
)
from agriphyto_schema.utils import clean_nomenclature_name, pandera_to_json

logger = getLogger(__name__)
logger.setLevel("DEBUG")


def map_type(x):
    """
    Map Excel type to Pandera type using MAP_TYPES dictionary."""
    for k, v in MAP_TYPES.items():
        if isinstance(x, str) and k.lower() in x.lower():
            return v
    return "string"


def parse_nomenclatures(db_name: str) -> dict:
    """
    Parse nomenclatures / modalities from the data dictionary.
    For now, adapted to RA2020 structure.

    Parameters
    ----------
    db_name : str
        The name of the data dictionary (e.g. "RA2020").

    Returns
    -------
    dict
        A dictionary mapping variable names to lists of allowed categories.
    """
    filepath2dico = AVAILABLE_DICOS[db_name]["filename"]
    sheet_name_modalites = AVAILABLE_DICOS[db_name]["modalites_sheet"]
    skiprows_modalites = AVAILABLE_DICOS[db_name]["skiprows_modalites"]
    modalites_df = pd.read_excel(
        DIR2DICO / filepath2dico,
        sheet_name=sheet_name_modalites,
        skiprows=skiprows_modalites,
    )
    cols_to_use = AVAILABLE_DICOS[db_name]["modalites_cols_to_use"]
    modalites_df.rename(columns=cols_to_use, inplace=True)
    # La colonne variable contient à la fois les noms de variables et les modalités. Elle ne peut être vide. On filtre donc les lignes vides.
    modalites_df = modalites_df[
        modalites_df[COLNAME_VARIABLE].notna()
    ].reset_index(drop=True)

    mask = modalites_df[COLNAME_TABLE].notna()
    starts = [*modalites_df.index[mask].tolist(), len(modalites_df)]

    modalites_dfs_clean = {}
    for i in range(len(starts) - 1):
        table_name = modalites_df.loc[starts[i], COLNAME_TABLE]
        var_name = modalites_df.loc[starts[i], COLNAME_VARIABLE]
        sub = modalites_df.iloc[starts[i] + 1 : starts[i + 1]].copy()[
            [COLNAME_VARIABLE, COLNAME_LIBELLE]
        ]
        sub.columns = modalites_df.iloc[starts[i], :][
            [COLNAME_VARIABLE, COLNAME_LIBELLE]
        ]  # use the header row
        sub = sub.dropna(how="all")  # drop empty lines
        if len(sub) > 0:
            var_name_clean = clean_nomenclature_name(var_name, table_name)
            # log if the cleaned name differs from the original
            var_name_check = var_name_clean.replace(f"{table_name}__", "")
            if  var_name_check != var_name:
                logger.warning(
                    f"!!! Variable name {var_name} differs from clean version {var_name_check}"
                )
            nomenclature = sub.reset_index(drop=True)
            modalites_dfs_clean[var_name_clean] = nomenclature
            path2modalites = (
                DIR2NOMENCLATURES / f"{db_name}__{var_name_clean}__categories.csv"
            )
            nomenclature.to_csv(path2modalites, index=False)
            logger.info(
                f"Variable {var_name_clean} nomenclature saved at {path2modalites}"
            )
    return modalites_dfs_clean


def parse_dico(db_name: str) -> None:
    """
    Parse an Excel data dictionary to create a pandera schema for data validation.

    Parameters
    ----------
    db_name : str
        The name of the data dictionary (e.g. "RA2020").

    Returns
    -------
    None
        Saves the pandera schema JSON files in agriphyto_schema/data/schemas/
    """
    if db_name not in AVAILABLE_DICOS:
        msg = f"Accepted db_name: {list(AVAILABLE_DICOS.keys())}. Got {db_name}"
        raise ValueError(msg)
    filepath2dico = AVAILABLE_DICOS[db_name]["filename"]
    sheet_name_variables = AVAILABLE_DICOS[db_name]["variable_sheet"]
    skiprows = AVAILABLE_DICOS[db_name]["skiprows"]
    cols_to_use = AVAILABLE_DICOS[db_name]["cols_to_use"]

    dico = pd.read_excel(
        DIR2DICO / filepath2dico,
        sheet_name=sheet_name_variables,
        skiprows=skiprows,
    )
    dico.rename(columns=cols_to_use, inplace=True)
    dico = dico[cols_to_use.values()]
    dico = dico.dropna(subset=[COLNAME_VARIABLE]).reset_index(drop=True)
    # Drop empty rows
    all_table_names = dico[COLNAME_TABLE].dropna().unique().tolist()
    logger.info(f"Found tables: {all_table_names}")
    # --- nomenclature / modalities
    modalities_dic = parse_nomenclatures(db_name)
    variables_w_modalities = list(modalities_dic.keys())
    dico[COLNAME_PANDERA_TYPE] = dico[COLNAME_TYPE].apply(map_type)
    for table_name in all_table_names:
        n_vars = dico[dico[COLNAME_TABLE] == table_name].shape[0]
        logger.info(f"Table {table_name} has {n_vars} variables")
        table_dico = dico[dico[COLNAME_TABLE] == table_name].reset_index(drop=True)
        # Sometimes the table name contains the db_name as prefix
        table_name_clean = table_name.replace(f"{db_name}_", "")
        # Assemble pandera schema with categories when available
        pandera_schema = pa.DataFrameSchema(
            columns={},
            strict=True,
            coerce=True,
            name=f"{db_name}__{table_name_clean}",
            description=f"Schema for table {table_name} from data dictionary {db_name}"
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
            varname_clean = clean_nomenclature_name(var_name, table_name_clean)
            if varname_clean in variables_w_modalities:
                # Add strict categories instead of nomenclature dic ?
                col_schema.metadata = {
                    "nomenclature": varname_clean
                }
            pandera_schema.columns[var_name] = col_schema
        pandera_to_json(pandera_schema, DIR2SCHEMA / f"{pandera_schema.name}.json")
        logger.info(
            f"Saved schema for table {table_name} to {DIR2SCHEMA / f'{pandera_schema.name}.json'}"
        )
