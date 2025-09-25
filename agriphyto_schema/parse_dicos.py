# %% 
import pandas as pd 
import pandera as pa
import json
from constants import DIR2DICO

# %% 
dico_name = "RA2020_Dictionnaire des variables_220415_CASD.xlsx"
sheet_name = "2_MODALITES_Variables"
dico = pd.read_excel(DIR2DICO / dico_name, sheet_name=sheet_name, skip_rows=4)
# Keep relevant columns and rename
dico = dico.iloc[:, :4]  # first 4 columns contain table, variable, label, type
dico.columns = ["TABLE", "VARIABLE", "LIBELLE", "TYPE"]

# Drop empty rows
dico = dico.dropna(subset=["VARIABLE"]).reset_index(drop=True)

# Simple mapping Excel type -> Pandera type
type_map = {
    "Numérique": "float",
    "Entier": "int",
    "Charactères": "string",
    "Booléen": "bool"
}

def map_type(x):
    for k, v in type_map.items():
        if isinstance(x, str) and k.lower() in x.lower():
            return v
    return "string"

dico["pandera_type"] = dico["TYPE"].apply(map_type)

# Build pandera schema in JSON format
pandera_schema = {
    "type": "DataFrameSchema",
    "columns": {
        row.VARIABLE: {"type": row.pandera_type}
        for _, row in dico.iterrows()
    }
}

# Save to JSON
with open("pandera_schema.json", "w", encoding="utf-8") as f:
    json.dump(pandera_schema, f, indent=2, ensure_ascii=False)

print("Schema saved to pandera_schema.json")
# %% 