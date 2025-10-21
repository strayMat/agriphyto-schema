import pandas as pd
import streamlit as st

from agriphyto_schema.app.utils import filter_dataframe, load_nomenclature, load_dico
from agriphyto_schema.constants import AGRIPHYTO_DICO_NAME, DIR2DATA, DIR2NOMENCLATURES, COLNAME_OUT_DB, COLNAME_OUT_NOMENCLATURE


# Layout stuff
def wide_space_default():
    st.set_page_config(layout="wide")


wide_space_default()


# Application
st.title("Dico Agriphyto 🥕")
st.markdown(
    """
    Voici le dictionnaire de données de la base Agriphyto.
    Il consolide les différents dictionnaires de données sources.
    """
)

# text_search = st.text_input("Search", value="")

dico = load_dico(DIR2DATA / f"{AGRIPHYTO_DICO_NAME}.csv")

# Filtrage des données
filtered_dico = filter_dataframe(dico)

# Database output logic
config = {
    "Preview": st.column_config.ImageColumn(),
    "Progress": st.column_config.ProgressColumn(),
}

# Affichage du dataframe principal avec selection des événements
event = st.dataframe(
    filtered_dico,
    column_config=config,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# Gestion des clics sur les lignes
if event.selection.rows:
    selected_row_index = event.selection.rows[0]

    # Récupération des informations de la ligne sélectionnée
    if selected_row_index < len(filtered_dico):
        selected_row = filtered_dico.iloc[selected_row_index]
        db_name = selected_row.get(COLNAME_OUT_DB, "")
        nomenclature_name = selected_row.get(COLNAME_OUT_NOMENCLATURE, "")
        nomenclature_file = f"{db_name}__{nomenclature_name}__categories.csv"
        path2nomenclature = DIR2NOMENCLATURES / nomenclature_file
        # Vérification si une nomenclature existe et n'est pas vide
        if nomenclature_name and str(nomenclature_name).strip() and str(nomenclature_name) != "nan":
            # Vérification de l'existence du fichier
            if path2nomenclature.is_file():
                st.subheader(f"📋 Nomenclature : {nomenclature_name}")

                # Chargement et affichage de la nomenclature
                nomenclature_df = load_nomenclature(path2nomenclature)
                st.dataframe(nomenclature_df, hide_index=True)
            else:
                st.info(f"💡 Aucun fichier de nomenclature trouvé pour `{path2nomenclature}`")
        else:
            st.info("💡 Sélectionnez une ligne avec une nomenclature pour afficher les détails.")

# Information d'aide
st.markdown("---")
st.markdown("💡 **Aide :** Cliquez sur une ligne de la colonne 'Nomenclature' pour afficher le détail des catégories.")