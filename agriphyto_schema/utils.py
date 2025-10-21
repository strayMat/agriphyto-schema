import json
from pathlib import Path

import pandera.pandas as pa
from pandas.api.types import is_numeric_dtype


def clean_nomenclature_name(var_name: str | float, table_name: str | None = None) -> str:
    """
    Clean variable name by replacing special characters.
    """
    if is_numeric_dtype(type(var_name)):
        var_name = str(var_name)
    var_name = var_name.replace("*", "star")
    var_name = var_name.replace(" ", "_")
    var_name = var_name.replace("-", "_")
    var_name = var_name.replace(";", "_")
    var_name = var_name.replace("<", "_")
    var_name = var_name.replace(">", "_")
    var_name = var_name.replace("(", "")
    var_name = var_name.replace(")", "")
    var_name = var_name.replace("\xa0", "_")
    if table_name:
        var_name = f"{table_name}__{var_name}"
    return var_name

# Workaround to save/load pandera schema with metadata
def pandera_to_json(schema: pa.DataFrameSchema, schema_path: Path):
    # move metadata into description field as json
    for col in schema.columns.values():
        metadata = col.metadata if hasattr(col, "metadata") else {}
        if col.description:
            metadata["description"] = col.description
        col.description = json.dumps(metadata)
        schema.columns[col.name] = col
    with open(schema_path, "w",encoding="utf-8") as f:
        f.write(schema.to_json(indent=4, ensure_ascii=False))

def pandera_from_json(schema_path: Path):
    schema = pa.DataFrameSchema.from_json(schema_path)
    # move description fields into metadata
    for col in schema.columns.values():
        if col.description:
            metadata = json.loads(col.description)
            if metadata:
                if "description" in metadata:
                    col.description = metadata.pop("description")
                col.metadata = metadata
                schema.columns[col.name] = col
    return schema
