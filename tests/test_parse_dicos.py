import pandas as pd
import pytest

from agriphyto_schema.constants import COLNAME_CODE, COLNAME_LIBELLE
from agriphyto_schema.data.parse_dicos import (
    clean_modalities,
    clean_nomenclature_name,
)


def test_clean_varname():
    """Test de la fonction clean_varname avec des caractères spéciaux."""
    # Test avec une chaîne contenant tous les caractères spéciaux traités
    input_name = "Test*Variable Name-with;special<>chars()\xa0"
    expected = "TeststarVariable_Name_with_special__chars_"
    result = clean_nomenclature_name(input_name)
    assert result == expected


@pytest.mark.parametrize(
    """raw_nomenclature,expected_length,expected_first_var,expected_first_label,
    expected_last_var,expected_last_label""",
    [
        (
            "1 - Option One\n2 - Option Two\n3 - Option Three",
            3,
            "1",
            "Option One",
            "3",
            "Option Three",
        ),
        (
            """1:Auto-produits
2:Achetés (coopérative, grossiste,...)
3:Achetés directement à des producteurs de plants
4:Achat sur internet
5:Produits par un autre agriculteur
6:Mélange""",
            6,
            "1",
            "Auto-produits",
            "6",
            "Mélange",
        ),
    ],
)
def test_clean_modalities(
    raw_nomenclature,
    expected_length,
    expected_first_var,
    expected_first_label,
    expected_last_var,
    expected_last_label,
):
    """Test clean_modalities with different delimiters and formats."""
    result = clean_modalities(raw_nomenclature)

    # Common assertions for all test cases
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == [COLNAME_CODE, COLNAME_LIBELLE]
    assert len(result) == expected_length

    # First row assertions
    assert result.iloc[0][COLNAME_CODE] == expected_first_var
    assert result.iloc[0][COLNAME_LIBELLE] == expected_first_label

    # Last row assertions
    assert result.iloc[-1][COLNAME_CODE] == expected_last_var
    assert result.iloc[-1][COLNAME_LIBELLE] == expected_last_label
