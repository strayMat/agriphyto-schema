# %%
%load_ext autoreload
%autoreload 2
import pandas as pd
import pandera as pa

from agriphyto_schema.constants import (
    COLNAME_OUT_DB,
    COLNAME_OUT_LIBELLE,
    COLNAME_OUT_NOMENCLATURE,
    COLNAME_OUT_PANDERA_TYPE,
    COLNAME_OUT_TABLE,
    COLNAME_OUT_VARIABLE,
    DIR2SCHEMA,
    AVAILABLE_DICOS,
    DIR2DATA,
    DIR2DICO

)
from agriphyto_schema.data.parse_dicos import parse_dico
# %% 
dico_name = "RA2020"
# %%
# Find where variable names appear
modalite_table_col = "TABLE"
var_col = "VARIABLE et MODALITES par table  "
label_col = "LIBELLE"

mask = modalites_df[modalite_table_col].notna()
starts = modalites_df.index[mask].tolist() + [len(modalites_df)]

modalites_dfs_clean = {}
for i in range(len(starts) - 1):
    var_name = modalites_df.loc[starts[i], var_col]
    sub = modalites_df.iloc[starts[i] + 1 : starts[i + 1]].copy()[[var_col, label_col]]
    sub.columns = modalites_df.iloc[starts[i], :][[var_col, label_col]]  # use the header row
    sub = sub.dropna(how="all")          # drop empty lines
    if len(sub) > 0:
        modalites_dfs_clean[var_name] = sub.reset_index(drop=True)

# %%
db_name = "RA2020"
table_name = "RA2020_IDADMIN"
schema_name = f"{db_name}_{table_name}"

schema = pa.DataFrameSchema.from_json(DIR2SCHEMA / f"{schema_name}.json")
print(schema)
# %%
# Create a dataframe from the pandera schema:
# extract

list(DIR2SCHEMA.iterdir())
# %%
