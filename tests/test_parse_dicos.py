import pandas as pd
import pytest

from agriphyto_schema.constants import COLNAME_CODE, COLNAME_LIBELLE
from agriphyto_schema.data.parse_dicos import clean_modalities


@pytest.mark.parametrize(
    "raw_nomenclature,expected_length,expected_first_var,expected_first_label,expected_last_var,expected_last_label",
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
            "A - Apple;B - Banana;C - Cherry",
            3,
            "A",
            "Apple",
            "C",
            "Cherry",
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
