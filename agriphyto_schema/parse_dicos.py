# %%
"""

Parse an Excel data dictionary to create a pandera schema for data validation.

Return a pandera schema JSON file for each table defined in the data dictionary.
A schema is named after : the data dictionary name (e.g. RA2020) and the table name.
It is saved in agriphyto_schema/schemas/
"""

import pandas as pd
import pandera as pa
import json
from constants import DIR2DICO, DIR2SCHEMA
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel("DEBUG")

# FIXME: move to constants
COLNAME_TABLE = "table"
COLNAME_VARIABLE = "variable"
COLNAME_LIBELLE = "label"
COLNAME_TYPE = "type"
COLNAME_PANDERA_TYPE = "pandera_type"
# Simple mapping Excel type -> Pandera type
MAP_TYPES = {"Numérique": "float", "Entier": "int", "Charactères": "string", "Booléen": "bool"}
# %%
dico_name = "RA2020"
filepath2dico = "RA2020_Dictionnaire des variables_220415_CASD.xlsx"
sheet_name_variables = "1_DICO_Variables"
skiprows = 3  # number of rows to skip at the beginning of the sheet
cols_to_use = {
    "TABLE_DIFFUSION": COLNAME_TABLE,
    "VARIABLE_DIFFUSION": COLNAME_VARIABLE,
    "LIBELLE": COLNAME_LIBELLE,
    "TYPE": COLNAME_TYPE,
}

dico = pd.read_excel(DIR2DICO / filepath2dico, sheet_name=sheet_name_variables, skiprows=skiprows)
dico.rename(columns=cols_to_use, inplace=True)
dico = dico[cols_to_use.values()]
dico = dico.dropna(subset=[COLNAME_VARIABLE]).reset_index(drop=True)
# Drop empty rows
table_names = dico[COLNAME_TABLE].dropna().unique().tolist()
logger.info(f"Found tables: {table_names}")
# %%
# TODO: add modalities
# --- nomenclature / modalities
# mods = pd.read_excel(filepath2dico, sheet_name="2_MODALITES_Variables")
# assuming it has at least columns: VARIABLE, MODALITE (adjust names if different)
# mods.columns = [c.upper() for c in mods.columns]
# %%


def map_type(x):
    for k, v in MAP_TYPES.items():
        if isinstance(x, str) and k.lower() in x.lower():
            return v
    return "string"


dico[COLNAME_PANDERA_TYPE] = dico[COLNAME_TYPE].apply(map_type)
# FIXME: need to create one schema for each table
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
            name=var_name, dtype=row.get(COLNAME_PANDERA_TYPE), nullable=True, title=row.get(COLNAME_LIBELLE)
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
        with open(DIR2SCHEMA / f"{pandera_schema.name}.json", "w", encoding="utf-8") as f:
            json.dump(pandera_schema.to_json(indent=4), f, ensure_ascii=False)

# %%
