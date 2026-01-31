"""
Cours 003: Clean Code - Imports Dupliques
==========================================
CORRIGE - Solution Complete

Ce fichier contient la version PROPRE.
Compare avec ton exercice pour voir les differences.

Les imports sont:
- Uniques (pas de doublons)
- Regroupes en haut du fichier
- Ordonnes selon PEP 8
"""

# ============================================================================
# IMPORTS PROPRES ET ORGANISES
# ============================================================================

# 1. Bibliotheque standard (ordre alphabetique)
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Modification de sys.path (si necessaire, apres l'import)
sys.path.append(str(Path(__file__).parent.parent))

# 2. Bibliotheques tierces (aucune dans cet exemple)
# import requests
# import numpy as np

# 3. Imports locaux (aucun dans cet exemple)
# from .models import User
# from ..utils import helpers


# ============================================================================
# CODE METIER
# ============================================================================

DATABASE_PATH = Path(__file__).parent / "data" / "app.db"
CONFIG_FILE = "config.json"


def load_config():
    """Charge la configuration depuis un fichier JSON."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def get_current_time() -> str:
    """Retourne l'heure actuelle formatee."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_data(data: Dict, filename: str) -> bool:
    """Sauvegarde des donnees en JSON."""
    try:
        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False


def log_action(action: str) -> None:
    """Log une action avec timestamp."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {action}")


# ============================================================================
# ANALYSEUR D'IMPORTS (identique a l'exercice)
# ============================================================================

def analyze_imports():
    """Analyse les imports du fichier pour detecter les doublons."""
    import ast
    import inspect

    print("="*60)
    print("COURS 003 - CORRIGE - Analyse des Imports")
    print("="*60)
    print()

    source_file = inspect.getfile(inspect.currentframe())
    with open(source_file, 'r') as f:
        source_code = f.read()

    tree = ast.parse(source_code)

    imports = []
    import_lines = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                imports.append(module_name)
                if module_name not in import_lines:
                    import_lines[module_name] = []
                import_lines[module_name].append(node.lineno)

        elif isinstance(node, ast.ImportFrom):
            module_name = f"from {node.module}" if node.module else "from ."
            for alias in node.names:
                full_import = f"{module_name} import {alias.name}"
                imports.append(full_import)
                if full_import not in import_lines:
                    import_lines[full_import] = []
                import_lines[full_import].append(node.lineno)

    duplicates = []
    dispersed = []

    for module, lines in import_lines.items():
        if len(lines) > 1:
            duplicates.append((module, lines))

    for module, lines in import_lines.items():
        for line in lines:
            if line > 50:
                dispersed.append((module, line))

    print("Imports trouves:")
    print("-" * 40)
    for module, lines in sorted(import_lines.items()):
        status = "❌ DUPLIQUE" if len(lines) > 1 else "✓"
        lines_str = ", ".join(str(l) for l in lines)
        print(f"  {status} {module} (ligne(s): {lines_str})")
    print()

    errors = []
    warnings = []

    if duplicates:
        print("🔴 IMPORTS DUPLIQUES:")
        print("-" * 40)
        for module, lines in duplicates:
            print(f"  ✗ '{module}' importe {len(lines)} fois (lignes: {lines})")
            errors.append(f"Import duplique: {module}")
        print()

    if dispersed:
        print("🟡 IMPORTS DISPERSES:")
        print("-" * 40)
        for module, line in dispersed:
            print(f"  ⚠ '{module}' a la ligne {line} (devrait etre en haut)")
            warnings.append(f"Import disperse: {module} ligne {line}")
        print()

    print("="*60)
    print("RESULTAT DE L'ANALYSE")
    print("="*60)
    print()

    if errors:
        print(f"🔴 ERREURS ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
        print()

    if warnings:
        print(f"🟡 WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")
        print()

    print("="*60)
    if errors:
        print("❌ ANALYSE ECHOUEE")
    elif warnings:
        print("⚠️  ANALYSE PASSEE AVEC WARNINGS")
    else:
        print("✅ ANALYSE PASSEE - Imports propres!")

    print("="*60)

    return len(errors) == 0


# ============================================================================
# EXPLICATION DE LA CORRECTION
# ============================================================================

def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Les imports etaient dupliques et disperses dans le fichier:

    import os           # Ligne 10
    import sys          # Ligne 11
    ...
    import sys          # Ligne 45 - DUPLIQUE!
    import os           # Ligne 46 - DUPLIQUE!
    ...
    from pathlib import Path  # Ligne 60 - DUPLIQUE!

CORRECTION:
-----------
Tous les imports regroupes en haut, sans doublons:

    # Bibliotheque standard
    import json
    import os
    import sys
    from datetime import datetime
    from pathlib import Path
    from typing import Dict, List, Optional

    # Modification sys.path apres import
    sys.path.append(...)

    # Reste du code...

REGLES PEP 8:
-------------
1. Imports en haut du fichier (apres docstring/comments)
2. Un import par ligne
3. Ordre: standard -> tiers -> local
4. Ligne vide entre chaque groupe

OUTIL RECOMMANDE:
-----------------
    pip install isort
    isort mon_fichier.py  # Corrige automatiquement!
============================================================
""")


if __name__ == "__main__":
    analyze_imports()
    print()
    show_explanation()
