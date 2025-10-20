import pandas as pd
import streamlit as st

from agriphyto_schema.app.utils import filter_dataframe
from agriphyto_schema.constants import AGRIPHYTO_DICO_NAME, DIR2DATA


# Layout stuff
def wide_space_default():
    st.set_page_config(layout="wide")


wide_space_default()


# Utils
@st.cache_data  # allow caching (mainly useful for development)
def load_dico():
    return pd.read_csv(DIR2DATA / f"{AGRIPHYTO_DICO_NAME}.csv")


# Application
st.title("Dico Agriphyto 🥕")
st.markdown(
    """
    Voici le dictionnaire de données de la base Agriphyto.
    Il consolide les différents dictionnaires de données sources.
    """
)

# text_search = st.text_input("Search", value="")

dico = load_dico()
# Database output logic
config = {
    "Preview": st.column_config.ImageColumn(),
    "Progress": st.column_config.ProgressColumn(),
}
st.dataframe(filter_dataframe(dico), column_config=config, hide_index=True)
# AwesomeTable(dico, show_search=True, show_order=True) # streamlit-awesome-table do the trick but it needs to be patched so I donot use it : patch is in AwsesomeTable init, line 3 `from pandas import json_normalize #from pandas.io.json import json_normalize`
