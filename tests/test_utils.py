import tempfile
from pathlib import Path

import pandera.pandas as pa

from agriphyto_schema.utils import (
    clean_nomenclature_name,
    pandera_from_json,
    pandera_to_json,
)


def test_clean_varname():
    """Test de la fonction clean_varname avec des caractères spéciaux."""
    # Test avec une chaîne contenant tous les caractères spéciaux traités
    input_name = "Test*Variable Name-with;special<>chars()\xa0"
    expected = "TeststarVariable_Name_with_special__chars_"
    result = clean_nomenclature_name(input_name)
    assert result == expected

def test_pandera_to_from_json():
    """Test de la fonction pandera_from_json pour charger un schéma depuis JSON."""
    # Créer un schéma pandera simple
    original_schema = pa.DataFrameSchema({
        "test_col": pa.Column(pa.Int, description="Test column", metadata={"unit": "kg"})
    })

    # Utiliser un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)

    try:
        # Sauvegarder le schéma
        pandera_to_json(original_schema, temp_path)

        # Charger le schéma depuis JSON
        loaded_schema = pandera_from_json(temp_path)

        # Vérifier que le schéma chargé a les mêmes colonnes
        assert "test_col" in loaded_schema.columns
        assert loaded_schema.columns["test_col"].description == "Test column"
        assert loaded_schema.columns["test_col"].metadata == {"unit": "kg"}
    finally:
        # Nettoyer le fichier temporaire
        if temp_path.exists():
            temp_path.unlink()
