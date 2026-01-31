"""
Cours 001: Bug Silencieux - Variable Non Initialisee
=====================================================
EXERCICE - Code a corriger

Niveau: Debutant
Duree: 30-45 minutes

INSTRUCTIONS:
-------------
1. Ce fichier contient un bug silencieux
2. Lance le script pour voir les tests echouer
3. Trouve et corrige le bug
4. Les tests doivent tous passer

INDICE:
-------
Le bug se manifeste quand on appelle get_content_items() SANS filtres.
Cherche une variable qui pourrait ne pas etre initialisee...

Pour lancer les tests:
    python 001-bug-where_clause-silencieux_exercice.py
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple
from dataclasses import dataclass


# ============================================================================
# MODELES DE DONNEES (ne pas modifier)
# ============================================================================

@dataclass
class ContentFilter:
    """Filtres pour la recherche de contenu"""
    content_type: str = None      # 'video' ou 'transcript'
    search_query: str = None      # Recherche dans le titre
    page: int = 1                 # Page actuelle
    per_page: int = 10            # Items par page


@dataclass
class ContentItem:
    """Un item de contenu (video ou transcript)"""
    id: str
    title: str
    type: str
    created_at: datetime
    status: str


# ============================================================================
# FONCTION A CORRIGER
# ============================================================================

async def get_content_items(
    db_path: str,
    filters: ContentFilter
) -> Tuple[List[ContentItem], int]:
    """
    Recupere les items de contenu avec pagination et filtres.

    Args:
        db_path: Chemin vers la base de donnees SQLite
        filters: Filtres a appliquer (content_type, search_query, pagination)

    Returns:
        Tuple[List[ContentItem], int]: Liste des items et total count

    BUG CONNU:
        Cette fonction retourne [], 0 quand aucun filtre n'est applique,
        meme si la base de donnees contient des donnees.

    VOTRE MISSION:
        Trouvez et corrigez le bug!
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            base_query = """
                SELECT 'video' as type, title, created_at FROM videos
                UNION ALL
                SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
            """

            # Construction des conditions WHERE
            where_clause = ""  # FIX: Initialiser where_clause AVANT le if
            where_conditions = []
            params = []

            if filters.content_type:
                where_conditions.append("type = ?")
                params.append(filters.content_type)

            if filters.search_query:
                where_conditions.append("title LIKE ?")
                params.append(f"%{filters.search_query}%")

            # Construction de la requete finale
            if where_conditions:
                where_clause = " WHERE " + " AND ".join(where_conditions)
                full_query = f"SELECT * FROM ({base_query}) content{where_clause}"
            else:
                where_clause = ""
                full_query = f"SELECT * FROM ({base_query}) content"

            # Compte total
            count_query = f"SELECT COUNT(*) FROM ({full_query}) counted"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # Resultats pagines
            offset = (filters.page - 1) * filters.per_page
            query = f"""
                SELECT type, title, created_at, 'active' as status
                FROM (
                    SELECT 'video' as type, title, created_at FROM videos
                    UNION ALL
                    SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
                ) content
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """

            params.extend([filters.per_page, offset])
            cursor.execute(query, params)

            items = []
            for row in cursor.fetchall():
                items.append(ContentItem(
                    id=f"{row[0]}_{hash(row[1])}",
                    title=row[1],
                    type=row[0],
                    created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                    status=row[3]
                ))

            return items, total_count

    except Exception as e:
        print(f"[ERROR] Failed to get content items: {e}")
        return [], 0


# ============================================================================
# TESTS DE VALIDATION (ne pas modifier)
# ============================================================================

def run_tests():
    """Execute les tests de validation."""
    import asyncio
    import tempfile
    import os

    print("="*60)
    print("COURS 001 - Tests de Validation")
    print("="*60)
    print()

    # Creer une base de donnees temporaire
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        # Setup: creer les tables et ajouter des donnees
        with sqlite3.connect(test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE videos (
                    title TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE transcripts (
                    video_title TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("INSERT INTO videos VALUES (?, ?)",
                ("Test Video 1", "2026-01-10T10:00:00"))
            cursor.execute("INSERT INTO videos VALUES (?, ?)",
                ("Test Video 2", "2026-01-10T11:00:00"))
            cursor.execute("INSERT INTO transcripts VALUES (?, ?)",
                ("Test Transcript", "2026-01-10T12:00:00"))
            conn.commit()

        passed = 0
        failed = 0

        # Test 1: Sans filtres (LE TEST QUI ECHOUE AVEC LE BUG)
        print("Test 1: Appel sans filtres")
        print("-" * 40)
        filters_empty = ContentFilter()
        items, total = asyncio.run(get_content_items(test_db, filters_empty))

        if total == 3 and len(items) == 3:
            print("✓ PASSE: Retourne 3 items")
            passed += 1
        else:
            print(f"✗ ECHOUE: Attendu 3 items, recu {total} (total), {len(items)} (liste)")
            print("  INDICE: Le bug est ici! Pourquoi ca retourne 0?")
            failed += 1
        print()

        # Test 2: Avec filtre content_type
        print("Test 2: Filtre par type 'video'")
        print("-" * 40)
        filters_video = ContentFilter(content_type="video")
        items, total = asyncio.run(get_content_items(test_db, filters_video))

        if total == 2:
            print("✓ PASSE: Retourne 2 videos")
            passed += 1
        else:
            print(f"✗ ECHOUE: Attendu 2 videos, recu {total}")
            failed += 1
        print()

        # Test 3: Avec filtre search_query
        print("Test 3: Recherche 'Transcript'")
        print("-" * 40)
        filters_search = ContentFilter(search_query="Transcript")
        items, total = asyncio.run(get_content_items(test_db, filters_search))

        if total == 1:
            print("✓ PASSE: Retourne 1 transcript")
            passed += 1
        else:
            print(f"✗ ECHOUE: Attendu 1 transcript, recu {total}")
            failed += 1
        print()

        # Resume
        print("="*60)
        print(f"RESULTAT: {passed}/3 tests passes")
        print("="*60)

        if failed > 0:
            print()
            print("Le bug n'est pas encore corrige!")
            print("Indice: Regarde la variable 'where_clause'...")
            print()
        else:
            print()
            print("FELICITATIONS! Tous les tests passent!")
            print("Tu as corrige le bug avec succes!")
            print()

    finally:
        os.unlink(test_db)


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
