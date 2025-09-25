# %% 
from agriphyto_schema.constants import DIR2SCHEMA
import pandera as pa
# %% 
schema_name = "RA2020"
schema_ = pa.DataFrameSchema.from_json(DIR2SCHEMA/f"{schema_name}.json")
# %%
print(schema_.to_json())
# %%