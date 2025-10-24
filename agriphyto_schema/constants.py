import os
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DIR2ROOT = Path(__file__).parent.parent.absolute()

DIR2DATA = DIR2ROOT / "data"
DIR2DICO = DIR2DATA / "raw"
DIR2SCHEMA = DIR2DATA / "schemas"
DIR2NOMENCLATURES = DIR2DATA / "nomenclatures"


COLNAME_TABLE = "table"
COLNAME_VARIABLE = "variable"
COLNAME_LIBELLE = "label"
COLNAME_TYPE = "type"
COLNAME_NOMENCLATURE = "nomenclature"
COLNAME_PANDERA_TYPE = "pandera_type"

# Simple mapping Excel type -> Pandera type
MAP_TYPES = {
    "Numérique": "float",
    "Entier": "int",
    "Charactères": "string",
    "Booléen": "bool",
}

# Configurations for loaded dictionaries
AVAILABLE_DICOS = {
    "RA2020": {
        "filename": "RA2020_Dictionnaire des variables_220415_CASD.xlsx",
        "variable_sheet": "1_DICO_Variables",
        "skiprows": 3,
        "modalites_sheet": "2_MODALITES_Variables",
        "skiprows_modalites": 2,
        "cols_to_use": {
            "TABLE_DIFFUSION": COLNAME_TABLE,
            "VARIABLE_DIFFUSION": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
        },
        "modalites_cols_to_use": {
            "TABLE": COLNAME_TABLE,
            "VARIABLE et MODALITES par table  ": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
        },
        "encoding": "latin1",
    },
    "PHYTOVITI2016": {
        "filename": "Pratiques_phytosanitaires_en_viticulture_-_2016.csv",
        "skiprows": 9,
        "encoding": "utf-8-sig",
        "parser": "dico_from_casd_csv",
    },
}
CASD_BOOL_MODALITIES = ['"0 - Non";"1 - Oui"']
USELESS_MODALITIES = [*CASD_BOOL_MODALITIES]
# Output dictionary columns
COLNAME_OUT_DB = "Database"
COLNAME_OUT_TABLE = "Table"
COLNAME_OUT_VARIABLE = "Variable"
COLNAME_OUT_PANDERA_TYPE = "Type"
COLNAME_OUT_LIBELLE = "Label"
COLNAME_OUT_NOMENCLATURE = "Nomenclature"
COLNAMES_OUTPUT = [
    COLNAME_OUT_DB,
    COLNAME_OUT_TABLE,
    COLNAME_OUT_VARIABLE,
    COLNAME_OUT_LIBELLE,
    COLNAME_OUT_PANDERA_TYPE,
    COLNAME_OUT_NOMENCLATURE,
]

AGRIPHYTO_DICO_NAME = "agriphyto_data_dictionary"
