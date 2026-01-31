"""
Cours 003: Clean Code - Imports Dupliques
==========================================
EXERCICE - Code a corriger

Niveau: Debutant
Duree: 15-20 minutes

INSTRUCTIONS:
-------------
1. Ce fichier contient des imports dupliques
2. Lance le script pour voir l'analyse
3. Corrige les imports
4. L'analyse doit passer sans erreurs

PROBLEMES A TROUVER:
--------------------
- Imports qui apparaissent plusieurs fois
- Imports disperses dans le fichier
- Ordre des imports non-standard

Pour lancer l'analyse:
    python exercice.py
"""

# ============================================================================
# IMPORTS - Regroupes en haut du fichier, sans doublons
# ============================================================================

# Standard library imports (ordre alphabetique)
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuration du path (apres les imports)
sys.path.append(str(Path(__file__).parent.parent))

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
# ANALYSEUR D'IMPORTS (ne pas modifier)
# ============================================================================

def analyze_imports():
    """Analyse les imports du fichier pour detecter les doublons."""
    import ast
    import inspect

    print("="*60)
    print("COURS 003 - Analyse des Imports")
    print("="*60)
    print()

    # Lire le fichier source
    source_file = inspect.getfile(inspect.currentframe())
    with open(source_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # Parser le code
    tree = ast.parse(source_code)

    # Collecter les imports
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

    # Detecter les doublons
    duplicates = []
    dispersed = []

    for module, lines in import_lines.items():
        if len(lines) > 1:
            duplicates.append((module, lines))

    # Detecter les imports disperses (pas dans les 50 premieres lignes)
    for module, lines in import_lines.items():
        for line in lines:
            if line > 50:
                dispersed.append((module, line))

    # Afficher les resultats
    print("Imports trouves:")
    print("-" * 40)
    for module, lines in sorted(import_lines.items()):
        status = "[X] DUPLIQUE" if len(lines) > 1 else "[OK]"
        lines_str = ", ".join(str(l) for l in lines)
        print(f"  {status} {module} (ligne(s): {lines_str})")
    print()

    errors = []
    warnings = []

    if duplicates:
        print("[ERROR] IMPORTS DUPLIQUES:")
        print("-" * 40)
        for module, lines in duplicates:
            print(f"  [X] '{module}' importe {len(lines)} fois (lignes: {lines})")
            errors.append(f"Import duplique: {module}")
        print()

    if dispersed:
        print("[WARN] IMPORTS DISPERSES:")
        print("-" * 40)
        for module, line in dispersed:
            print(f"  [!] '{module}' a la ligne {line} (devrait etre en haut)")
            warnings.append(f"Import disperse: {module} ligne {line}")
        print()

    # Resume
    print("="*60)
    print("RESULTAT DE L'ANALYSE")
    print("="*60)
    print()

    if errors:
        print(f"[ERROR] ERREURS ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
        print()

    if warnings:
        print(f"[WARN] WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")
        print()

    total_issues = len(errors) + len(warnings)

    print("="*60)
    if errors:
        print("[FAIL] ANALYSE ECHOUEE - Corrige les imports dupliques!")
        print()
        print("INDICES:")
        print("  1. Garde un seul import par module")
        print("  2. Regroupe tous les imports en haut du fichier")
        print("  3. Suis l'ordre: standard -> tiers -> local")
    elif warnings:
        print("[WARN] ANALYSE PASSEE AVEC WARNINGS")
        print("  Les imports devraient etre regroupes en haut du fichier.")
    else:
        print("[OK] ANALYSE PASSEE - Imports propres!")
        print()
        print("FELICITATIONS!")
        print("Tous les imports sont uniques et bien organises.")

    print("="*60)

    return len(errors) == 0


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_imports()
