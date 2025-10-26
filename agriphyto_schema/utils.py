import json
from pathlib import Path

import pandera.pandas as pa

from agriphyto_schema.constants import AVAILABLE_DICOS


# Workaround to save/load pandera schema with metadata
def pandera_to_json(schema: pa.DataFrameSchema, schema_path: Path):
    # move metadata into description field as json
    for col in schema.columns.values():
        metadata = col.metadata if hasattr(col, "metadata") else {}
        if col.description:
            metadata["description"] = col.description
        col.description = json.dumps(metadata)
        schema.columns[col.name] = col
    with open(schema_path, "w", encoding="utf-8") as f:
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


def check_db_name(db_name: str) -> None:
    """
    Check if the provided db_name is in AVAILABLE_DICOS.
    Parameters
    ----------
    db_name : str

        The name of the data dictionary (e.g. "RA2020").
    Raises
    -------
    ValueError
        If db_name is not in AVAILABLE_DICOS.
    """
    if db_name not in AVAILABLE_DICOS:
        msg = f"Accepted db_name: {list(AVAILABLE_DICOS.keys())}. Got {db_name}"
        raise ValueError(msg)

