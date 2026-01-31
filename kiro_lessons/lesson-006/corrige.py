"""
Cours 006: Clean Code - Duplication de Fichiers
================================================
CORRIGE - Solution Complete

Ce fichier montre le projet APRES resolution de la duplication.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass
from typing import List


# ============================================================================
# PROJET APRES CORRECTION
# ============================================================================

@dataclass
class SimulatedFile:
    """Represente un fichier simule."""
    name: str
    content: str
    is_imported: bool = False


# Projet APRES suppression du doublon
PROJECT_FILES_CLEAN = {
    "src/api/routes/admin.py": SimulatedFile(
        name="admin.py",
        content='''
import os
from fastapi import APIRouter

router = APIRouter()

# ============================================
# CORRECTION: Ameliorations fusionnees depuis admin_secure.py
# ============================================
admin_token = os.getenv("ADMIN_TOKEN")
if not admin_token:
    raise ValueError("ADMIN_TOKEN environment variable is required")
# ============================================

@router.get("/admin/status")
async def get_status():
    return {"status": "ok", "secure": True}
''',
        is_imported=True
    ),

    # admin_secure.py a ete SUPPRIME!

    "src/main.py": SimulatedFile(
        name="main.py",
        content='''
from fastapi import FastAPI
from src.api.routes import admin

app = FastAPI()
app.include_router(admin.router)
''',
        is_imported=True
    ),
}


def analyze_clean_project():
    """Analyse le projet apres correction."""

    print("="*60)
    print("COURS 006 - CORRIGE - Projet Sans Duplication")
    print("="*60)
    print()

    # Afficher la structure du projet
    print("Structure du projet (apres correction):")
    print("-" * 40)
    for path in sorted(PROJECT_FILES_CLEAN.keys()):
        file = PROJECT_FILES_CLEAN[path]
        print(f"  {path}")
    print()

    # Verifier qu'il n'y a plus de doublon
    print("Verification:")
    print("-" * 40)

    has_duplicate = any("_secure" in path or "_backup" in path
                       for path in PROJECT_FILES_CLEAN.keys())

    if has_duplicate:
        print("❌ Des fichiers dupliques existent encore!")
    else:
        print("✅ Aucun fichier duplique!")
        print("✅ admin_secure.py a ete supprime!")
        print("✅ Les ameliorations ont ete fusionnees dans admin.py!")

    print()

    # Montrer le fichier corrige
    print("Contenu de admin.py (apres fusion):")
    print("-" * 40)
    print(PROJECT_FILES_CLEAN["src/api/routes/admin.py"].content)

    print()
    print("="*60)
    print("✅ PROJET PROPRE - Pas de duplication!")
    print("="*60)

    return not has_duplicate


def show_git_commands():
    """Affiche les commandes Git utilisees pour la correction."""
    print("""
============================================================
COMMANDES GIT UTILISEES
============================================================

# 1. Voir les differences entre les fichiers
git diff --no-index admin.py admin_secure.py

# 2. Appliquer les corrections a admin.py
# (fait manuellement en editant le fichier)

# 3. Supprimer le fichier duplique
git rm src/api/routes/admin_secure.py

# 4. Ajouter les modifications
git add src/api/routes/admin.py

# 5. Commiter avec un message clair
git commit -m "fix: Remove duplicate admin_secure.py

- Merged security improvements into admin.py
- ADMIN_TOKEN now required (no unsafe fallback)
- Removed unused admin_secure.py file"

============================================================
""")


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Deux fichiers quasi-identiques existaient:
  - admin.py (utilise)
  - admin_secure.py (NON utilise)

admin_secure.py contenait une amelioration de securite
qui n'avait jamais ete appliquee au fichier principal.

SOLUTION:
---------
1. Identifier les ameliorations dans admin_secure.py:
   - Validation obligatoire de ADMIN_TOKEN
   - Pas de fallback dangereux "dev-token-unsafe"

2. Fusionner ces ameliorations dans admin.py:
   AVANT:  admin_token = os.getenv("ADMIN_TOKEN", "dev-token-unsafe")
   APRES:  admin_token = os.getenv("ADMIN_TOKEN")
           if not admin_token:
               raise ValueError("ADMIN_TOKEN required")

3. Supprimer admin_secure.py:
   git rm src/api/routes/admin_secure.py

RESULTAT:
---------
- Un seul fichier admin.py
- Avec les ameliorations de securite
- Pas de confusion sur quel fichier modifier
- Pas de divergence possible

LECON:
------
- Utiliser Git au lieu de creer des copies
- Fusionner rapidement les branches/ameliorations
- Supprimer les fichiers obsoletes
============================================================
""")


if __name__ == "__main__":
    analyze_clean_project()
    print()
    show_git_commands()
    show_explanation()
