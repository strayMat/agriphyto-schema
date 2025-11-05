from pathlib import Path

import pandas as pd
import streamlit as st

from agriphyto_schema.constants import (
    COLNAME_LIBELLE,
    COLNAME_OUT_DB,
    COLNAME_OUT_LIBELLE,
    COLNAME_OUT_TABLE,
    COLNAME_OUT_VARIABLE,
)


# credits: https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/
def filter_dt_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    df = df.copy()
    modification_container = st.container()

    with modification_container:
        _, right = st.columns((1, 20))

        # Filter in the label and variable columns using text
        user_text_input = right.text_input(
            f"Match exact ou regex sur les colonnes {COLNAME_OUT_LIBELLE} ou {COLNAME_OUT_VARIABLE} (non sensible à la casse)",
        )
        if user_text_input:
            df = df[
                (
                    df[COLNAME_OUT_LIBELLE]
                    .astype(str)
                    .str.lower()
                    .str.contains(user_text_input.strip())
                )
                | (
                    df[COLNAME_OUT_VARIABLE]
                    .astype(str)
                    .str.lower()
                    .str.contains(user_text_input.strip())
                )
            ]
        # Optional filters
        modify = st.checkbox(
            "Ajout d'un filtre par table ou par base de données"
        )
        if modify:
            # Filter on database
            db_choices = list(df[COLNAME_OUT_DB].unique())
            user_cat_input = right.multiselect(
                f"Values for {COLNAME_OUT_DB}",
                db_choices,
                default=list(df[COLNAME_OUT_DB].unique()),
            )
            df = df[df[COLNAME_OUT_DB].isin(user_cat_input)]
            # Filter on Table
            user_cat_input = right.multiselect(
                f"Values for {COLNAME_OUT_TABLE}",
                df[COLNAME_OUT_TABLE].unique(),
                default=list(df[COLNAME_OUT_TABLE].unique()),
            )
            df = df[df[COLNAME_OUT_TABLE].isin(user_cat_input)]

    return df


def filter_dt_nomenclatures(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter by regex on COLNAME_LIBELLE

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    df = df.copy()
    modification_container = st.container()

    with modification_container:
        _, right = st.columns((1, 20))

        # Filter in the label and variable columns using text
        user_text_input = right.text_input(
            f"Match exact ou regex sur la colonne {COLNAME_LIBELLE} (non sensible à la casse)",
        )
        if user_text_input:
            df = df[
                (
                    df[COLNAME_LIBELLE]
                    .astype(str)
                    .str.lower()
                    .str.contains(user_text_input.strip())
                )
            ]
    return df


# Loading fonctions with caching
@st.cache_data  # allow caching (mainly useful for development)
def load_dico(path2dico: str | Path):
    return pd.read_csv(path2dico)


@st.cache_data
def load_nomenclature(
    path2nomenclature: str | Path,
) -> pd.DataFrame:
    # Lecture du fichier CSV
    df = pd.read_csv(path2nomenclature)
    return df
