#!/usr/bin/env python3
"""
Entrée de commande principale du projet agriphyto.

Ce script se trouve dans le répertoire ``bin`` afin de pouvoir être
exécuté directement depuis la ligne de commande (ex. ``bin/cli.py``).

Il invoque la fonction ``main`` du module ``agriphyto_schema.parse_cli``,
qui se charge de parser les dictionnaires de données définis dans
``agriphyto_schema.constants.AVAILABLE_DICOS`` et d’enregistrer les
résultats au format JSON.

Utilisation
-----------

    python bin/cli.py -d BTS_2021_Etablissements

ou, si le répertoire ``bin`` est dans le PATH :

    ./bin/cli.py -d BTS_2021_Etablissements
"""

import sys
from pathlib import Path

# Ajoute le répertoire racine du projet au PYTHONPATH afin que les imports
# relatifs fonctionnent même lorsque le script est exécuté depuis ``bin``.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def _run():
    """Lance le parser via le module ``agriphyto_schema.parse_cli``."""
    from agriphyto_schema.parse_cli import main as parse_main
    parse_main()

if __name__ == "__main__":
    _run()
