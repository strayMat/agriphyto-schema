# %% 
import pandas as pd 
import pandera as pa
import json
from constants import DIR2DICO, DIR2SCHEMA

# %% 
dico_name = "RA2020"
filepath2dico = "RA2020_Dictionnaire des variables_220415_CASD.xlsx"
sheet_name = "1_DICO_Variables"
dico = pd.read_excel(DIR2DICO / filepath2dico, sheet_name=sheet_name, skiprows=4)
# Keep relevant columns and rename
dico = dico.iloc[:, :4]  # first 4 columns contain table, variable, label, type
dico.columns = ["TABLE", "VARIABLE", "LIBELLE", "TYPE"]
# TODO: add modalities
# --- nomenclature / modalities
#mods = pd.read_excel(filepath2dico, sheet_name="2_MODALITES_Variables")
# assuming it has at least columns: VARIABLE, MODALITE (adjust names if different)
#mods.columns = [c.upper() for c in mods.columns]
# %%
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
#FIXME: need to create one schema for each table
# Build allowed categories dict from modalities
# categories = (
#     mods.groupby("VARIABLE")["MODALITE"]
#     .apply(lambda s: sorted(set(s.dropna().astype(str))))
#     .to_dict()
# )

# Assemble pandera schema with categories when available
pandera_schema = {
    "type": "DataFrameSchema",
    "columns": {}
}

for _, row in dico.iterrows():
    col_schema = {"type": row.pandera_type}
    # if row.VARIABLE in categories:
    #     col_schema["checks"] = {
    #         "isin": categories[row.VARIABLE]  # Pandera supports Check.isin([...])
    #     }
    pandera_schema["columns"][row.VARIABLE] = col_schema

# Save to JSON
with open(DIR2SCHEMA/f"{dico_name}.json", "w", encoding="utf-8") as f:
    json.dump(pandera_schema, f, indent=2, ensure_ascii=False)

# %% 