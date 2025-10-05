# %%
from agriphyto_schema.constants import DIR2SCHEMA
import pandera as pa

# %%
schema_name = "RA2020"
schema = pa.DataFrameSchema.from_json(DIR2SCHEMA / f"{schema_name}.json")
# %%
print(schema.to_json())
# %%
