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
# %%
dico_name = "RA2020"
# %%

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
