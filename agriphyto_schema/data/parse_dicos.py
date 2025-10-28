"""
#FIXME: put this in the cli rather than here.
Parse an Excel data dictionary to create a pandera schema for data validation of
the data dictionary.

The parser functions return a pandera schema JSON file for each table defined in
the data dictionary.

A schema is named after : the data dictionary name (e.g. RA2020) and the table name.
Schema are saved in agriphyto_schema/schemas/
"""

import re
from logging import getLogger
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandas.api.types import is_numeric_dtype

from agriphyto_schema.constants import (
    AVAILABLE_DICOS,
    CASD_BOOL_MODALITIES,
    COLNAME_CODE,
    COLNAME_LIBELLE,
    COLNAME_NOMENCLATURE,
    COLNAME_NOMENCLATURE_2,
    COLNAME_OUT_DB,
    COLNAME_PANDERA_TYPE,
    COLNAME_TABLE,
    COLNAME_TYPE,
    COLNAME_VARIABLE,
    DIR2DICO,
    DIR2NOMENCLATURES,
    DIR2SCHEMA,
    FILENAME_NOMENCLATURES,
    MAP_TYPES,
    USELESS_MODALITIES,
)
from agriphyto_schema.utils import check_db_name, pandera_to_json

logger = getLogger(__name__)
logger.setLevel("DEBUG")


# typing utils
def map_type(x):
    """
    Map Excel type to Pandera type using MAP_TYPES dictionary."""
    for k, v in MAP_TYPES.items():
        if isinstance(x, str) and k.lower() in x.lower():
            return v
    return "string"


def infer_type_from_varname(var_name: str) -> str:
    """Infer the Pandera type from the variable name.

    Args:
        var_name (str): The variable name.

    Returns:
        str: The inferred Pandera type.
    """
    pandera_type = "string"  # default
    if any(
        pattern in var_name.upper()
        for pattern in [
            "NB",
            "COEF",
            "SUPP",
            "DIST",
            "DENIT",
            "REND",
            "PRIX",
            "AGE",
            "DOSE",
            "QTE",
            "QDOSE",
        ]
    ):
        pandera_type = "float"
    elif any(
        pattern in var_name.upper()
        for pattern in ["IDENT", "CODE", "SIRET", "AMM", "ANNEE", "AN"]
    ):
        pandera_type = "string"
    return pandera_type


# Nomenclature parsers and utils
def remove_db_from_nomenclature(db_name: str):
    path2all_nomenclatures = DIR2NOMENCLATURES / FILENAME_NOMENCLATURES
    if path2all_nomenclatures.exists():
        all_nomenclatures = pd.read_csv(path2all_nomenclatures)
        all_nomenclatures[all_nomenclatures[COLNAME_OUT_DB] != db_name].to_csv(
            path2all_nomenclatures, index=False
        )


def clean_nomenclature_name(
    var_name: str | float, table_name: str | None = None
) -> str:
    """
    Clean variable name by replacing special characters.
    Args:
        var_name (str | float): Original variable name
        table_name (str | None): Optional table name to prefix
    Returns:
        str: Cleaned variable name prefixed by table name if provided.
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


# util to clean modality columns
def clean_modalities(  # noqa: C901
    raw_nomenclature_row: str, code_first: bool = True
) -> pd.DataFrame:
    """
    Clean and parse modalities from a raw nomenclature string.

    Parameters
    ----------
    raw_nomenclature_row : str
        The raw nomenclature string containing modalities to be parsed.
    code_first : bool, optional
        Whether the code appears before the label in the modalities, by default True.
        Eg. "1 - Label" vs "Label - 1".
    Returns
    -------
    pd.DataFrame
        A DataFrame with columns 'variable' and 'libelle' containing
        the cleaned modalities (code and label pairs). If no modalities are found, returns an empty
        DataFrame with the correct columns.
    """
    cleaned_modalites = []
    modality_separators = ["\n", "|", ";", ",", " ou "]
    # First, split the raw nomenclature based on different delimiters
    splitted_nomenclatures = None
    for sep in modality_separators:
        if (sep in raw_nomenclature_row) and (splitted_nomenclatures is None):
            splitted_nomenclatures = raw_nomenclature_row.split(sep)

    # If no split happened, try a regex split directly getting back code and labels based on the
    # formatting of PK surveys dictionaries:
    pattern = r"(\d{1,3}):(.*?)(?=(?:\d{1,3}:)|$)"
    regex_search = re.search(pattern, raw_nomenclature_row)
    if (splitted_nomenclatures is None) and (regex_search is not None):
        nomenclature = pd.DataFrame(
            re.findall(pattern, raw_nomenclature_row),
            columns=[COLNAME_CODE, COLNAME_LIBELLE],
        )
    else:
        if splitted_nomenclatures is None:
            splitted_nomenclatures = [raw_nomenclature_row]
        # Process each modality
        code_label_separator = [" - ", "=", ":"]
        if len(splitted_nomenclatures) == 0:
            return pd.DataFrame(columns=[COLNAME_CODE, COLNAME_LIBELLE])

        for mod in splitted_nomenclatures:
            if mod and mod.strip() != "":
                mod_clean = mod.strip().replace('"', "")
                # Split on different separators to separate code from label
                split_done = False
                for sep in code_label_separator:
                    if (sep in mod_clean) & (not split_done):
                        split_done = True
                        code, label = mod_clean.split(sep, 1)
                        cleaned_modalites.append({
                            COLNAME_CODE: code.strip(),
                            COLNAME_LIBELLE: label.strip(),
                        })
                if not split_done:
                    # no code label separtor found
                    cleaned_modalites.append({
                        COLNAME_CODE: mod_clean,
                        COLNAME_LIBELLE: mod_clean,
                    })
        # Create DataFrame with proper column names
        nomenclature = pd.DataFrame(cleaned_modalites)
    # Switch column order if nomenclature are of the form:  label - code
    if len(nomenclature) > 0:
        if not code_first:
            nomenclature = nomenclature[[COLNAME_LIBELLE, COLNAME_CODE]]
            nomenclature.columns = [COLNAME_CODE, COLNAME_LIBELLE]
    else:
        # Return empty DataFrame with correct columns
        nomenclature = pd.DataFrame(columns=[COLNAME_CODE, COLNAME_LIBELLE])
    return nomenclature


# nomenclature parsers
def nomenclature_from_nomenclature_sheet(
    db_name: str,
    filepath2dico: Path,
    nomenclature_sheet: str,
    skiprows_nomenclature: str,
    cols_to_use_nomenclature: dict | None,
) -> dict[str, pd.DataFrame]:
    """
    Parse nomenclatures / modalities from a separate nomenclature sheet in the data dictionary.
    Adaptée pour le RA2020.

    Parameters
    ----------
    db_name : str

        The name of the data dictionary (e.g. "RA2020").
    filepath2dico : Path
        The path to the data dictionary Excel file.
    nomenclature_sheet : str
        The name of the sheet containing nomenclatures.
    skiprows_nomenclature : str
        The number of rows to skip before reading the nomenclature sheet.
    Returns
    -------
    dict
        A dictionary mapping variable names to data frames containing the code-label mappings for
        each data modality.
    """
    remove_db_from_nomenclature(db_name)
    modalites_df = pd.read_excel(
        DIR2DICO / filepath2dico,
        sheet_name=nomenclature_sheet,
        skiprows=skiprows_nomenclature,
    )
    modalites_df.rename(columns=cols_to_use_nomenclature, inplace=True)
    # La colonne variable contient à la fois les codes et les libellés des modalités.
    # Elle ne peut être vide. On filtre donc les lignes vides.
    modalites_df = modalites_df[modalites_df[COLNAME_CODE].notna()].reset_index(
        drop=True
    )

    mask = modalites_df[COLNAME_TABLE].notna()
    starts = [*modalites_df.index[mask].tolist(), len(modalites_df)]

    all_modalities_df = {}
    for i in range(len(starts) - 1):
        table_name = modalites_df.loc[starts[i], COLNAME_TABLE]
        var_name = modalites_df.loc[starts[i], COLNAME_CODE]
        raw_modalities = modalites_df.iloc[
            starts[i] + 1 : starts[i + 1]
        ].copy()[[COLNAME_CODE, COLNAME_LIBELLE]]
        raw_modalities.columns = [COLNAME_CODE, COLNAME_LIBELLE]
        raw_modalities = raw_modalities.dropna(how="all")  # drop empty lines
        if len(raw_modalities) > 0:
            var_name_clean = clean_nomenclature_name(var_name, table_name)
            # log if the cleaned name differs from the original
            var_name_check = var_name_clean.replace(f"{table_name}__", "")
            if var_name_check != var_name:
                logger.warning(
                    f"!!! Variable name {var_name} differs from clean version {var_name_check}"
                )
            modalities_df = raw_modalities.reset_index(drop=True)
            all_modalities_df[var_name_clean] = modalities_df
            #
            modalities_df[COLNAME_TABLE] = table_name
            modalities_df[COLNAME_VARIABLE] = var_name_clean
            modalities_df[COLNAME_OUT_DB] = db_name
            modalities_df = modalities_df[
                [
                    COLNAME_OUT_DB,
                    COLNAME_TABLE,
                    COLNAME_VARIABLE,
                    COLNAME_CODE,
                    COLNAME_LIBELLE,
                ]
            ]

            path2modalites = DIR2NOMENCLATURES / FILENAME_NOMENCLATURES
            if not path2modalites.exists():
                # write header
                modalities_df.to_csv(path2modalites, index=False, mode="w")
            else:
                modalities_df.to_csv(
                    path2modalites, index=False, mode="a", header=False
                )
            logger.info(
                f"Variable {var_name_clean} nomenclature appended in {path2modalites}"
            )
    return all_modalities_df


def nomenclature_from_variable_sheet(
    db_name: str,
    filepath2dico: Path,
    variable_sheet: str,
    cols_to_use: dict,
    skiprows_nomenclature: int,
) -> dict[str, pd.DataFrame]:
    """
    Parameters
    ----------
    db_name : str
        The name of the data dictionary (e.g. "RA2020").
    filepath2dico : Path
        The path to the data dictionary Excel file.
    variable_sheet : str

        The name of the sheet containing variables.
    cols_to_use : dict
        A dictionary mapping original column names to standardized column names.
    skiprows : int
        The number of rows to skip before reading the variable sheet.
    Returns
    -------
    dict
        A dictionary mapping variable names to data frames containing the code-label mappings
        for each data modality.
        Save nomenclatures into one centralized csv file by append mode in agriphyto_schema/data/nomenclatures/all_nomenclatures.csv
    """
    remove_db_from_nomenclature(db_name)
    if COLNAME_NOMENCLATURE not in cols_to_use.values():
        msg = """This function only handles behavior 1) where modalities are in the same sheet as
        variables."""
        raise ValueError(msg)
    dico = pd.read_excel(
        DIR2DICO / filepath2dico,
        sheet_name=variable_sheet,
        skiprows=skiprows_nomenclature,
    )
    dico.rename(columns=cols_to_use, inplace=True)
    dico = dico[cols_to_use.values()]
    # Ensure TABLE column exists, else create it with variable_sheet
    if COLNAME_TABLE not in dico.columns:
        dico[COLNAME_TABLE] = variable_sheet
    dico = dico.dropna(subset=[COLNAME_VARIABLE]).reset_index(drop=True)
    # Extract nomenclatures
    all_modalities_df = {}
    dico_w_modalities = dico[
        dico[COLNAME_NOMENCLATURE].notna() & (dico[COLNAME_NOMENCLATURE] != "")
    ].reset_index(drop=True)
    for _, row in dico_w_modalities.iterrows():
        var_name = row[COLNAME_VARIABLE]
        raw_nomenclature_row = row[COLNAME_NOMENCLATURE]
        modalities_df = clean_modalities(raw_nomenclature_row, code_first=True)
        if len(modalities_df) > 0:
            table_name = row[COLNAME_TABLE]
            var_name_clean = clean_nomenclature_name(var_name, table_name)
            all_modalities_df[var_name_clean] = modalities_df
            modalities_df[COLNAME_TABLE] = table_name
            modalities_df[COLNAME_VARIABLE] = var_name_clean
            modalities_df[COLNAME_OUT_DB] = db_name
            modalities_df = modalities_df[
                [
                    COLNAME_OUT_DB,
                    COLNAME_TABLE,
                    COLNAME_VARIABLE,
                    COLNAME_CODE,
                    COLNAME_LIBELLE,
                ]
            ]
            path2modalites = DIR2NOMENCLATURES / FILENAME_NOMENCLATURES
            if not path2modalites.exists():
                # write header
                modalities_df.to_csv(path2modalites, index=False, mode="w")
            else:
                modalities_df.to_csv(
                    path2modalites, index=False, mode="a", header=False
                )
            logger.info(
                f"Variable {var_name_clean} nomenclature saved at {path2modalites}"
            )

    return all_modalities_df


def parse_dico(db_name: str) -> None:
    parser = AVAILABLE_DICOS[db_name].get("parser")

    if parser:
        eval(parser)(db_name)  # noqa: S307
    else:
        logger.error(f"No parser found for {db_name}")


def dico_from_excel(db_name: str) -> None:
    """
    Parse an Excel data dictionary to create a pandera schema for data validation.
    For each variable, output in the pandera schema :
    - the variable name,
    - the name of the origin table,
    - the pandera type,
    - the nomenclature / modalities of the variable if available.

    Parse nomenclatures / modalities from the data dictionary.
    Two behaviors are supported:
    - 1) either the modalities are in the same sheet as the variables,
    - 2) the modalities are in a separate sheet.
    The behavior is set to 1) if the COLNAME_NOMENCLATURE is in the cols_to_use of the
    AVAILABLE_DICOS[db_name] configuration else 2).

    Parameters
    ----------
    db_name : str
        The name of the data dictionary (e.g. "RA2020").

    Returns
    -------
    None
        Saves the pandera schema JSON files in agriphyto_schema/data/schemas/
        Saves the nomenclature CSV files in agriphyto_schema/data/nomenclatures/
    """
    check_db_name(db_name)
    filepath2dico = AVAILABLE_DICOS[db_name]["filename"]
    sheet_name_variables = AVAILABLE_DICOS[db_name]["variable_sheet"]
    cols_to_use = AVAILABLE_DICOS[db_name]["cols_to_use"]
    skiprows = AVAILABLE_DICOS[db_name].get("skiprows", 0)
    # force a list if only on sheet name is provided
    if not isinstance(sheet_name_variables, list):
        sheet_name_variables = [sheet_name_variables]

    for sheet_name in sheet_name_variables:
        logger.info(f"Processing sheet {sheet_name} of {filepath2dico}")
        dico = pd.read_excel(
            DIR2DICO / filepath2dico,
            sheet_name=sheet_name,
            skiprows=skiprows,
        )
        dico.rename(columns=cols_to_use, inplace=True)
        new_cols = cols_to_use.values()
        # Handle cases where nomenclatures are in two columns
        if COLNAME_NOMENCLATURE_2 in cols_to_use.values():
            dico[COLNAME_NOMENCLATURE] = dico[COLNAME_NOMENCLATURE].fillna(
                dico[COLNAME_NOMENCLATURE_2]
            )
            new_cols = [
                col for col in new_cols if col != COLNAME_NOMENCLATURE_2
            ]
        # Ensure TABLE column exists, else create it with sheet_name
        if COLNAME_TABLE not in dico.columns:
            dico[COLNAME_TABLE] = sheet_name
            new_cols = [*new_cols, COLNAME_TABLE]
        dico = dico[new_cols]
        dico = dico.dropna(subset=[COLNAME_VARIABLE]).reset_index(drop=True)
        # Drop empty rows
        all_table_names = dico[COLNAME_TABLE].dropna().unique().tolist()
        logger.info(f"Found tables: {all_table_names}")
        # Extract nomenclatures
        if COLNAME_NOMENCLATURE in cols_to_use.values():
            # behavior 1) nomenclatures in the same sheet as variables
            modalities_dic = nomenclature_from_variable_sheet(
                db_name=db_name,
                filepath2dico=filepath2dico,
                variable_sheet=sheet_name,
                cols_to_use=cols_to_use,
                skiprows_nomenclature=skiprows,
            )
        else:
            # behavior 2) nomenclatures in a separate sheet
            nomenclature_sheet = AVAILABLE_DICOS[db_name]["nomenclature_sheet"]
            skiprows_nomenclature = AVAILABLE_DICOS[db_name][
                "skiprows_nomenclature"
            ]
            cols_to_use_nomenclature = AVAILABLE_DICOS[db_name][
                "cols_to_use_nomenclature"
            ]
            modalities_dic = nomenclature_from_nomenclature_sheet(
                db_name=db_name,
                filepath2dico=filepath2dico,
                nomenclature_sheet=nomenclature_sheet,
                skiprows_nomenclature=skiprows_nomenclature,
                cols_to_use_nomenclature=cols_to_use_nomenclature,
            )

        dico[COLNAME_PANDERA_TYPE] = dico[COLNAME_TYPE].apply(map_type)
        for table_name in all_table_names:
            n_vars = dico[dico[COLNAME_TABLE] == table_name].shape[0]
            logger.info(f"Table {table_name} has {n_vars} variables")
            table_dico = dico[dico[COLNAME_TABLE] == table_name].reset_index(
                drop=True
            )
            # Dirty exception for RA2020 where table names have the RA2020 as prefix
            table_name_clean = table_name.replace("RA2020_", "")
            # Assemble pandera schema with categories when available
            pandera_schema = pa.DataFrameSchema(
                columns={},
                strict=True,
                coerce=True,
                name=f"{db_name}__{table_name_clean}",
                description=f"Schema for table {table_name} from data dictionary {db_name}",
            )
            # Add columns
            for _, row in table_dico.iterrows():
                var_name = row.get(COLNAME_VARIABLE)
                col_schema = pa.Column(
                    name=var_name,
                    dtype=row.get(COLNAME_PANDERA_TYPE),
                    nullable=True,
                    title=row.get(COLNAME_LIBELLE),
                )
                varname_clean = clean_nomenclature_name(
                    var_name, table_name_clean
                )
                if varname_clean in modalities_dic:
                    # Add strict categories instead of nomenclature dic ?
                    col_schema.metadata = {"nomenclature": varname_clean}
                pandera_schema.columns[var_name] = col_schema
            pandera_to_json(
                pandera_schema, DIR2SCHEMA / f"{pandera_schema.name}.json"
            )
            logger.info(
                f"""Saved schema for table {table_name} to
                {DIR2SCHEMA / f"{pandera_schema.name}.json"}"""
            )


# CASD CSV parser
def detect_table_section_from_casd_csv(
    filepath2dico: str,
    skiprows: int,
    encoding: str,
) -> dict:
    """
    Detect table sections in a CASD CSV data dictionary.
    Parameters
    ----------
    filepath2dico : str
        The path to the CASD CSV data dictionary file.
    skiprows : int
        The number of rows to skip before reading the CSV file. These lines are often a short
        description of the data source as well as blank lines before the first table.
    encoding : str
        The encoding of the CSV file.
    Returns
    -------
    dict
        A dictionary mapping table names to their description and variable line ranges.
    """
    # Read the CSV file
    with open(DIR2DICO / filepath2dico, encoding=encoding) as f:
        lines = f.readlines()

    # First loop: detect table_name, table_description, start and end of variable names
    table_sections = {}

    # Start processing after skipping the specified number of lines
    i = skiprows
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Look for the header pattern: "Nom de la variable";Libellé;Modalités
        if line.startswith('"Nom de la variable";Libellé;Modalités'):
            # Detection of the table is made by detecting this line
            # Two lines before there is the table_description
            table_description = ""
            if i >= 2:
                table_description = lines[i - 2].strip().replace('"', "")

            # Three lines before there is the table_name
            table_name = ""
            if i >= 3:
                table_name = lines[i - 3].strip()

            # Find the end of this table section (next empty line or next table)
            start_line = i + 1  # Variables start after the header
            end_line = len(lines)  # Default to end of file

            j = start_line
            while j < len(lines):
                current_line = lines[j].strip()
                # End of table section: empty line followed by potential next table
                if not current_line:
                    # Check if we have reached the end or if there's a next table section
                    k = j + 1
                    while k < len(lines) and not lines[k].strip():
                        k += 1  # Skip multiple empty lines

                    # If we find another table name or end of file, this is the end
                    if k >= len(lines) or (
                        k + 3 < len(lines)
                        and lines[k + 3]
                        .strip()
                        .startswith('"Nom de la variable";Libellé;Modalités')
                    ):
                        end_line = j
                        break
                j += 1

            table_sections[table_name] = {
                "table_description": table_description,
                "start_line": start_line,
                "end_line": end_line,
            }

            # Move to after this table section
            i = end_line
        else:
            i += 1

    logger.info(f"Found tables: {list(table_sections.keys())}")
    return table_sections


# FIXME: refactor to have the same logic for nomenclature building and saving as in dico_from_excel
def dico_from_casd_csv(db_name: str) -> None:
    """
    Parse a csv data dictionary from
    `CASD source <https://www.casd.eu/donnees-utilisees-sur-le-casd/>`_ to create a pandera schema
    for data validation.
    For each variable, output in the pandera schema :
    - the variable name,
    - the name of the origin table,
    - the pandera type,
    - the nomenclature / modalities of the variable if available.

    Parse nomenclatures / modalities from the data dictionary. In the CASD csv, modalities are
    always in a "third" column (they use the same ";" separator for the modalities so I have to
    force all remaining values after the first two columns into a third one).

    Parameters
    ----------
    db_name : str
        The name of the data dictionary (e.g. "PHYTOVITI2016").

    Returns
    -------
    None
        Saves the pandera schema JSON files in agriphyto_schema/data/schemas/
        Saves the nomenclature CSV files in agriphyto_schema/data/nomenclatures/
    """
    check_db_name(db_name)
    remove_db_from_nomenclature(db_name)

    # Load configuration from AVAILABLE_DICOS
    filepath2dico = AVAILABLE_DICOS[db_name]["filename"]
    skiprows = AVAILABLE_DICOS[db_name]["skiprows"]
    encoding = AVAILABLE_DICOS[db_name]["encoding"]
    # first loop on the csv to detect table sections
    table_sections = detect_table_section_from_casd_csv(
        filepath2dico=filepath2dico,
        skiprows=skiprows,
        encoding=encoding,
    )
    # Second loop: parse variables for each table section
    with open(DIR2DICO / filepath2dico) as f:
        lines = f.readlines()
    for table_name, section in table_sections.items():
        table_description = section["table_description"]
        start_line = section["start_line"]
        end_line = section["end_line"]

        logger.info(
            f"Processing table {table_name} with variables from line {start_line} to {end_line}"
        )

        # Read the table variables using pandas, forcing only the first 3 columns
        table_variables_lines = lines[start_line:end_line]
        # split on ';' and put all nomenclature modalities in the third column
        table_variables = pd.DataFrame([
            x.strip().split(";") for x in table_variables_lines
        ])
        table_variables[2] = table_variables.iloc[:, 2:].apply(
            lambda x: ";".join(x.dropna().astype(str)), axis=1
        )
        table_variables = table_variables.iloc[:, :3]
        table_variables.columns = [
            COLNAME_VARIABLE,
            COLNAME_LIBELLE,
            COLNAME_NOMENCLATURE,
        ]
        # Clean and process the data
        table_variables = table_variables.dropna(
            subset=["variable"]
        ).reset_index(drop=True)
        table_variables = table_variables[
            table_variables["variable"].str.strip() != ""
        ].reset_index(drop=True)
        # clean variable and label columns
        table_variables[COLNAME_VARIABLE] = (
            table_variables[COLNAME_VARIABLE].str.strip().str.replace('"', "")
        )
        table_variables[COLNAME_LIBELLE] = (
            table_variables[COLNAME_LIBELLE].str.strip().str.replace('"', "")
        )
        # add type inference
        table_variables[COLNAME_TYPE] = table_variables[COLNAME_VARIABLE].apply(
            infer_type_from_varname
        )
        mask_binary_nomenclature = table_variables[COLNAME_NOMENCLATURE].isin(
            CASD_BOOL_MODALITIES
        )
        table_variables.loc[mask_binary_nomenclature, COLNAME_TYPE] = "bool"
        # clean nomenclature column
        table_variables[COLNAME_NOMENCLATURE] = table_variables[
            COLNAME_NOMENCLATURE
        ].fillna("")
        table_variables[COLNAME_NOMENCLATURE] = table_variables[
            COLNAME_NOMENCLATURE
        ].apply(lambda x: None if x in USELESS_MODALITIES else x)

        # Create nomenclature dictionary for this table
        table_variables_w_modalities = table_variables[
            table_variables[COLNAME_NOMENCLATURE].notna()
            & (table_variables[COLNAME_NOMENCLATURE] != "")
        ].reset_index(drop=True)

        # extract nomenclature and create files
        for _, row in table_variables_w_modalities.iterrows():
            var_name = row[COLNAME_VARIABLE]
            raw_nomenclature_row = row[COLNAME_NOMENCLATURE]
            modalities_df = clean_modalities(
                raw_nomenclature_row, code_first=True
            )
            var_name_clean = clean_nomenclature_name(var_name, table_name)
            modalities_df[COLNAME_TABLE] = table_name
            modalities_df[COLNAME_VARIABLE] = var_name_clean
            modalities_df[COLNAME_OUT_DB] = db_name
            modalities_df = modalities_df[
                [
                    COLNAME_OUT_DB,
                    COLNAME_TABLE,
                    COLNAME_VARIABLE,
                    COLNAME_CODE,
                    COLNAME_LIBELLE,
                ]
            ]
            # Save nomenclature to CSV
            path2modalites = DIR2NOMENCLATURES / FILENAME_NOMENCLATURES
            if not path2modalites.exists():
                # write header
                modalities_df.to_csv(path2modalites, index=False, mode="w")
            else:
                modalities_df.to_csv(
                    path2modalites, index=False, mode="a", header=False
                )
            logger.info(
                f"Variable {var_name_clean} nomenclature saved at {path2modalites}"
            )

        # Create pandera schema
        pandera_schema = pa.DataFrameSchema(
            columns={},
            strict=True,
            coerce=True,
            name=f"{db_name}__{table_name}",
            description=f"""Schema for table {table_name} ({table_description})
        from data dictionary {db_name}""",
        )
        # Add columns to schema
        for var_info in table_variables.to_dict(orient="records"):
            var_name = var_info["variable"]
            col_schema = pa.Column(
                name=var_name,
                dtype=infer_type_from_varname(var_name),
                nullable=True,
                title=var_info[COLNAME_LIBELLE],
            )
            if (
                var_name
                in table_variables_w_modalities[COLNAME_VARIABLE].tolist()
            ):
                var_name_clean = clean_nomenclature_name(var_name, table_name)
                col_schema.metadata = {"nomenclature": var_name_clean}
            pandera_schema.columns[var_name] = col_schema
        # Save schema
        pandera_to_json(
            pandera_schema, DIR2SCHEMA / f"{pandera_schema.name}.json"
        )
        logger.info(
            f"Saved schema for table {table_name} to {DIR2SCHEMA / f'{pandera_schema.name}.json'}"
        )
