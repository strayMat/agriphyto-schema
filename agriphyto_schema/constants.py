import os
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DIR2ROOT = Path(__file__).parent.parent.absolute()

DIR2DATA = DIR2ROOT / "data"
DIR2DICO = DIR2DATA / "raw"
DIR2SCHEMA = DIR2DATA / "schemas"
DIR2NOMENCLATURES = DIR2DATA / "nomenclatures"

FILENAME_NOMENCLATURES = "all_nomenclatures.csv"

COLNAME_TABLE = "table"
COLNAME_VARIABLE = "variable"
COLNAME_LIBELLE = "label"
COLNAME_TYPE = "type"
COLNAME_NOMENCLATURE = "nomenclature"
COLNAME_CODE = "modality_code"
COLNAME_NOMENCLATURE_2 = (
    "nomenclature_2"  # sometimes two columns are used for nomenclature...
)
COLNAME_PANDERA_TYPE = "pandera_type"

# Simple mapping Excel type -> Pandera type
MAP_TYPES = {
    "Numérique": "float",
    "numérique": "float",
    "Decimal": "float",
    "NumericalCode": "int",
    "PositiveInteger": "int",
    "Comment": "string",
    "Integer": "int",
    "Entier": "int",
    "OuiNon": "bool",
    "Booléen": "bool",
    "Boolean": "bool",
    "String": "string",
    "Code": "string",
    "Charactères": "string",
    "Caractère": "string",
    "Chaîne": "string",
    "Date": "datetime64[ns]",
}

# Configurations for loaded dictionaries
# TODO: document this better or put this into a documented config class
AVAILABLE_DICOS = {
    # I replaced manually "IDENTIFICATIION" by "IDADMIN" in the nomenclature sheet to be consistent
    #  with the variable sheet
    "RA_2020": {
        "filename": "RA2020_Dictionnaire des variables_220415_CASD.xlsx",
        "variable_sheet": "1_DICO_Variables",
        "skiprows": 3,
        "nomenclature_sheet": "2_MODALITES_Variables",
        "skiprows_nomenclature": 2,
        "cols_to_use": {
            "TABLE_DIFFUSION": COLNAME_TABLE,
            "VARIABLE_DIFFUSION": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
        },
        "cols_to_use_nomenclature": {
            "TABLE": COLNAME_TABLE,
            "VARIABLE et MODALITES par table  ": COLNAME_CODE,
            "LIBELLE": COLNAME_LIBELLE,
        },
        "encoding": "latin1",
        "parser": "dico_from_excel",
    },
    "PHYTOVITI_2016": {
        "filename": "Pratiques_phytosanitaires_en_viticulture_-_2016.csv",
        "skiprows": 9,
        "encoding": "utf-8-sig",
        "parser": "dico_from_casd_csv",
    },
    "FIDELI_2020": {
        "filename": "Fichier_Démographique_sur_les_Logements_et_les_Individus_(FIDELI)_-_2022.csv",
        "skiprows": 6,
        "encoding": "utf-8-sig",
        "parser": "dico_from_casd_csv",
    },
    "PKPrairie_2011": {
        "filename": "Pratiques_culturales_en_prairie_-_2011.csv",
        "skiprows": 8,
        "encoding": "utf-8-sig",
        "parser": "dico_from_casd_csv",
    },
    "PhytoGC_2014": {
        "filename": "Pratiques_phytosanitaires_en_grandes_cultures_-_2014.csv",
        "skiprows": 8,
        "encoding": "utf-8-sig",
        "parser": "dico_from_casd_csv",
    },
    "Phytofruits_2018": {
        "filename": "Phytofruits18_dico_variables_casd.ods",
        "variable_sheet": "data",
        "cols_to_use": {
            "Fichier": COLNAME_TABLE,
            "NOM_variable": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
            "NOMENCLATURE": COLNAME_NOMENCLATURE,
        },
        "parser": "dico_from_excel",
    },
    "PKfruits_2015": {
        "filename": "20210726_PKfruits2015_dico_variables.ods",
        "variable_sheet": "data",
        "cols_to_use": {
            "Fichier": COLNAME_TABLE,
            "NOM_variable": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
            "VALEURS": COLNAME_NOMENCLATURE,
        },
        "parser": "dico_from_excel",
    },
    "PKLeg_2013": {
        "filename": "PKLEG13_DESC.ods",
        "variable_sheet": "Data",
        "cols_to_use": {
            "Fichier": COLNAME_TABLE,
            "Nom": COLNAME_VARIABLE,
            "Label": COLNAME_LIBELLE,
            "Type": COLNAME_TYPE,
            "Nomenc": COLNAME_NOMENCLATURE,
            "Filtre": COLNAME_NOMENCLATURE_2,
        },
        "parser": "dico_from_excel",
    },
    # I manually searched and replaced all ";" code-lable separators in the modalities column
    # with ":" to avoid confusion with the ";" used to separate modalities
    "PKViti_2019": {
        "filename": "PKViti2019_dico_variables_definitif.ods",
        "variable_sheet": [
            "PKViti2019_definitif",
            "PKViti2019_gest_enherb_definitif",
            "PKViti2019_ope_cult_definitif",
            "PKViti2019_IFT_trait_definitif",
            "MATACT_PKViti2019_definitif",
            "PKViti2019_AMM_SA",
        ],
        "cols_to_use": {
            "NOM": COLNAME_VARIABLE,
            "DESCRIPTION (avec éventuelle référence dans le questionnaire)": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
            "MODALITES": COLNAME_NOMENCLATURE,
        },
        "parser": "dico_from_excel",
    },
    # I manually searched and replaced all ";" code-lable separators in the modalities column
    # with ":" to avoid confusion with the ";" used to separate modalities
    "PKGC_2017": {
        "filename": "PKGC2017_dico_variables.ods",
        "variable_sheet": "PKGC2017_dicoVar_global",
        "cols_to_use": {
            "NOM_VARIABLE": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
            "NOMENCLATURE": COLNAME_NOMENCLATURE,
        },
        "parser": "dico_from_excel",
    },
    "Phytoleg_2018": {
        "filename": "20210930_DOC_BSVA_Dictionnaire_variables_Phytolégumes2018.ods",
        "variable_sheet": [
            "20210930_Phytolegumes2018_definitive",
            "20210930_Phytolegumes2018_TTMT_Phyto_definitive",
            "20210930_Phytolegumes2018_TTMT_MATACT",
        ],
        "cols_to_use": {
            "NOM": COLNAME_VARIABLE,
            "LIBELLE": COLNAME_LIBELLE,
            "TYPE": COLNAME_TYPE,
            "NOMENCLATURE": COLNAME_NOMENCLATURE,
        },
        "parser": "dico_from_excel",
    },
}
CASD_BOOL_MODALITIES = ['"0 - Non";"1 - Oui"', '"1 - Oui";"0 - Non"', "oui/non"]
USELESS_MODALITIES = [*CASD_BOOL_MODALITIES]
# Output dictionary columns
COLNAME_OUT_DB = "Database"
COLNAME_OUT_TABLE = "Table"
COLNAME_OUT_VARIABLE = "Variable"
COLNAME_OUT_PANDERA_TYPE = "Type"
COLNAME_OUT_LIBELLE = "Label"
COLNAME_OUT_NOMENCLATURE = "Nomenclature"
COLNAMES_OUTPUT = [
    COLNAME_OUT_DB,
    COLNAME_OUT_TABLE,
    COLNAME_OUT_VARIABLE,
    COLNAME_OUT_LIBELLE,
    COLNAME_OUT_PANDERA_TYPE,
    COLNAME_OUT_NOMENCLATURE,
]

AGRIPHYTO_DICO_NAME = "agriphyto_data_dictionary"
