# %%
import json

import pandera as pa

from agriphyto_schema.constants import DIR2SCHEMA

# %%
db_name = "RA2020"
table_name = "RA2020_IDADMIN"
schema_name = f"{db_name}_{table_name}"

schema = pa.DataFrameSchema.from_json(DIR2SCHEMA / f"{schema_name}.json")
print(schema)
# %%
