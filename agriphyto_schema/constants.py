import os
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DIR2ROOT = Path(__file__).parent.parent.absolute()

DIR2DATA = DIR2ROOT / "data"
DIR2DICO = DIR2DATA / "raw"
DIR2SCHEMA = DIR2DATA / "schemas"


COLNAME_TABLE = "table"
COLNAME_VARIABLE = "variable"
COLNAME_LIBELLE = "label"
COLNAME_TYPE = "type"
COLNAME_PANDERA_TYPE = "pandera_type"

# Simple mapping Excel type -> Pandera type
MAP_TYPES = {
    "Numérique": "float",
    "Entier": "int",
    "Charactères": "string",
    "Booléen": "bool",
}