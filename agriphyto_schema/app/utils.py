import pandas as pd
import streamlit as st

from agriphyto_schema.constants import (
    COLNAME_OUT_DB,
    COLNAME_OUT_LIBELLE,
    COLNAME_OUT_TABLE,
    COLNAME_OUT_VARIABLE,
)


# credits: https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
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
        left, right = st.columns((1, 20))

        # Filter in the label and variable columns using text
        user_text_input = right.text_input(
            f"Substring or regex in {COLNAME_OUT_LIBELLE} or {COLNAME_OUT_VARIABLE} (case insensitive)",
        )
        if user_text_input:
            df = df[
                (
                    df[COLNAME_OUT_LIBELLE]
                    .astype(str)
                    .str.lower()
                    .str.contains(user_text_input)
                )
                | (
                    df[COLNAME_OUT_VARIABLE]
                    .astype(str)
                    .str.lower()
                    .str.contains(user_text_input)
                )
            ]
        # Optional filters
        modify = st.checkbox("Add table or database filters")
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
