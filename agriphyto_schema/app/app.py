import streamlit as st

from agriphyto_schema.app.utils import (
    filter_dataframe,
    load_dico,
    load_nomenclature,
)
from agriphyto_schema.constants import (
    AGRIPHYTO_DICO_NAME,
    COLNAME_OUT_DB,
    COLNAME_OUT_NOMENCLATURE,
    COLNAME_TABLE,
    COLNAME_VARIABLE,
    DIR2DATA,
    DIR2NOMENCLATURES,
)


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
    selection_mode="single-row",
)

all_nomenclatures = load_nomenclature(
    DIR2NOMENCLATURES / "all_nomenclatures.csv"
)

# Gestion des clics sur les lignes
if event.selection.rows:
    selected_row_index = event.selection.rows[0]

    # Récupération des informations de la ligne sélectionnée
    if selected_row_index < len(filtered_dico):
        selected_row = filtered_dico.iloc[selected_row_index]
        db_name = selected_row.get(COLNAME_OUT_DB, "")
        clean_variable_name = selected_row.get(COLNAME_OUT_NOMENCLATURE, "")
        selected_nomenclature = all_nomenclatures[
            (all_nomenclatures[COLNAME_OUT_DB] == db_name)
            & (
                all_nomenclatures[COLNAME_TABLE]
                == selected_row.get(COLNAME_TABLE, "")
            )
            & (all_nomenclatures[COLNAME_VARIABLE] == clean_variable_name)
        ]

        # Vérification si une nomenclature existe et n'est pas vide
        if (
            clean_variable_name
            and str(clean_variable_name).strip()
            and (str(clean_variable_name) != "nan")
            and (len(selected_nomenclature) > 0)
        ):
            st.dataframe(selected_nomenclature, hide_index=True)
        else:
            st.info(
                "💡 Sélectionnez une ligne avec une nomenclature pour afficher les détails."
            )

# Information d'aide
st.markdown("---")
st.markdown(
    "💡 **Aide :** Cliquez sur une ligne de la colonne 'Nomenclature' pour afficher le détail des catégories."
)
