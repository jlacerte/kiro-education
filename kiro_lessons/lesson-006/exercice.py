"""
Cours 006: Clean Code - Duplication de Fichiers
================================================
EXERCICE - Detecter et resoudre la duplication

Niveau: Debutant
Duree: 20-30 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un projet avec des fichiers dupliques
2. Lance le script pour voir l'analyse
3. Identifie quel fichier est utilise vs. non utilise
4. Determine l'action a prendre

Pour lancer l'analyse:
    python exercice.py
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


# ============================================================================
# SIMULATION DE FICHIERS DUPLIQUES
# ============================================================================

@dataclass
class SimulatedFile:
    """Represente un fichier simule."""
    name: str
    content: str
    is_imported: bool = False


# Simulation du projet avec duplication
PROJECT_FILES = {
    "src/api/routes/admin.py": SimulatedFile(
        name="admin.py",
        content='''
import os
from fastapi import APIRouter

router = APIRouter()

# Version originale - UTILISEE
admin_token = os.getenv("ADMIN_TOKEN", "dev-token-unsafe")

@router.get("/admin/status")
async def get_status():
    return {"status": "ok"}
''',
        is_imported=True  # Ce fichier EST utilise dans main.py
    ),

    "src/api/routes/admin_secure.py": SimulatedFile(
        name="admin_secure.py",
        content='''
import os
from fastapi import APIRouter

router = APIRouter()

# Version amelioree - NON UTILISEE!
admin_token = os.getenv("ADMIN_TOKEN")
if not admin_token:
    raise ValueError("ADMIN_TOKEN environment variable is required")

@router.get("/admin/status")
async def get_status():
    return {"status": "ok", "secure": True}
''',
        is_imported=False  # Ce fichier N'EST PAS utilise!
    ),

    "src/main.py": SimulatedFile(
        name="main.py",
        content='''
from fastapi import FastAPI
from src.api.routes import admin  # <- Importe admin.py, PAS admin_secure.py!

app = FastAPI()
app.include_router(admin.router)
''',
        is_imported=True
    ),
}


def calculate_similarity(content1: str, content2: str) -> float:
    """Calcule un score de similarite entre deux contenus."""
    lines1 = set(content1.strip().split('\n'))
    lines2 = set(content2.strip().split('\n'))

    if not lines1 or not lines2:
        return 0.0

    intersection = lines1 & lines2
    union = lines1 | lines2

    return len(intersection) / len(union) * 100


def find_differences(content1: str, content2: str) -> List[Tuple[str, str, str]]:
    """Trouve les differences entre deux fichiers."""
    lines1 = content1.strip().split('\n')
    lines2 = content2.strip().split('\n')

    differences = []

    for i, (l1, l2) in enumerate(zip(lines1, lines2)):
        if l1 != l2:
            differences.append((f"Ligne {i+1}", l1.strip(), l2.strip()))

    # Lignes supplementaires
    if len(lines2) > len(lines1):
        for i, line in enumerate(lines2[len(lines1):], len(lines1)+1):
            differences.append((f"Ligne {i}", "(absente)", line.strip()))

    return differences


def analyze_duplicates():
    """Analyse le projet pour detecter les fichiers dupliques."""

    print("="*60)
    print("COURS 006 - Detection de Fichiers Dupliques")
    print("="*60)
    print()

    # Afficher la structure du projet
    print("Structure du projet simule:")
    print("-" * 40)
    for path in sorted(PROJECT_FILES.keys()):
        file = PROJECT_FILES[path]
        status = "✓ UTILISE" if file.is_imported else "✗ NON UTILISE"
        print(f"  {path}")
        print(f"      -> {status}")
    print()

    # Trouver les paires de fichiers similaires
    print("Analyse de similarite:")
    print("-" * 40)

    admin_file = PROJECT_FILES["src/api/routes/admin.py"]
    admin_secure_file = PROJECT_FILES["src/api/routes/admin_secure.py"]

    similarity = calculate_similarity(admin_file.content, admin_secure_file.content)
    print(f"  admin.py vs admin_secure.py: {similarity:.1f}% similaires")
    print()

    if similarity > 50:
        print("🔴 DUPLICATION DETECTEE!")
        print()
        print("  Fichiers concernes:")
        print("    - admin.py (UTILISE)")
        print("    - admin_secure.py (NON UTILISE)")
        print()

        # Montrer les differences
        print("Differences trouvees:")
        print("-" * 40)
        differences = find_differences(admin_file.content, admin_secure_file.content)

        for loc, old, new in differences[:5]:  # Limiter a 5
            print(f"  {loc}:")
            print(f"    admin.py:        {old[:50]}...")
            print(f"    admin_secure.py: {new[:50]}...")
            print()

        # Analyser les ameliorations
        print("="*60)
        print("ANALYSE DES AMELIORATIONS")
        print("="*60)
        print()

        if "raise ValueError" in admin_secure_file.content:
            print("✅ admin_secure.py contient une AMELIORATION:")
            print("   - Validation obligatoire de ADMIN_TOKEN")
            print("   - Pas de fallback dangereux")
            print()

        print("="*60)
        print("❌ DUPLICATION A RESOUDRE!")
        print("="*60)
        print()
        print("ACTIONS RECOMMANDEES:")
        print("-" * 40)
        print("""
  1. FUSIONNER les ameliorations de admin_secure.py dans admin.py

     # Dans admin.py, remplacer:
     admin_token = os.getenv("ADMIN_TOKEN", "dev-token-unsafe")

     # Par:
     admin_token = os.getenv("ADMIN_TOKEN")
     if not admin_token:
         raise ValueError("ADMIN_TOKEN required")

  2. SUPPRIMER admin_secure.py

     git rm src/api/routes/admin_secure.py

  3. COMMITER avec un message clair

     git commit -m "fix: Merge admin_secure.py into admin.py, remove duplicate"
""")

    else:
        print("✅ Aucune duplication problematique detectee!")

    return similarity < 50


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_duplicates()
