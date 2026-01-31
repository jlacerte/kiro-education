"""
Cours 001: Bug Silencieux - Variable Non Initialisee
=====================================================
CORRIGE - Solution Complete

Ce fichier contient la version CORRIGEE.
Compare avec ton exercice pour voir la difference.

La correction est sur UNE SEULE LIGNE (ligne 72).
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple
from dataclasses import dataclass


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class ContentFilter:
    """Filtres pour la recherche de contenu"""
    content_type: str = None
    search_query: str = None
    page: int = 1
    per_page: int = 10


@dataclass
class ContentItem:
    """Un item de contenu (video ou transcript)"""
    id: str
    title: str
    type: str
    created_at: datetime
    status: str


# ============================================================================
# FONCTION CORRIGEE
# ============================================================================

async def get_content_items(
    db_path: str,
    filters: ContentFilter
) -> Tuple[List[ContentItem], int]:
    """
    Recupere les items de contenu avec pagination et filtres.

    VERSION CORRIGEE - Le bug etait: where_clause non initialise
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            base_query = """
                SELECT 'video' as type, title, created_at FROM videos
                UNION ALL
                SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
            """

            # ========================================================
            # CORRECTION ICI: Initialiser where_clause AVANT le if
            # ========================================================
            where_clause = ""  # <-- LA LIGNE QUI MANQUAIT
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
                full_query = f"SELECT * FROM ({base_query}) content"
                # where_clause reste "" - plus de NameError!

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
            # Maintenant {where_clause} est toujours defini (soit "" soit " WHERE ...")

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
# TESTS DE VALIDATION
# ============================================================================

def run_tests():
    """Execute les tests pour confirmer que la correction fonctionne."""
    import asyncio
    import tempfile
    import os

    print("="*60)
    print("COURS 001 - CORRIGE - Validation")
    print("="*60)
    print()

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name

    try:
        with sqlite3.connect(test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE videos (title TEXT, created_at TEXT)")
            cursor.execute("CREATE TABLE transcripts (video_title TEXT, created_at TEXT)")
            cursor.execute("INSERT INTO videos VALUES (?, ?)",
                ("Test Video 1", "2026-01-10T10:00:00"))
            cursor.execute("INSERT INTO videos VALUES (?, ?)",
                ("Test Video 2", "2026-01-10T11:00:00"))
            cursor.execute("INSERT INTO transcripts VALUES (?, ?)",
                ("Test Transcript", "2026-01-10T12:00:00"))
            conn.commit()

        # Test 1: Sans filtres
        filters_empty = ContentFilter()
        items, total = asyncio.run(get_content_items(test_db, filters_empty))
        assert total == 3, f"Test 1 echoue: attendu 3, recu {total}"
        print("✓ Test 1: Sans filtres retourne 3 items")

        # Test 2: Filtre video
        filters_video = ContentFilter(content_type="video")
        items, total = asyncio.run(get_content_items(test_db, filters_video))
        assert total == 2, f"Test 2 echoue: attendu 2, recu {total}"
        print("✓ Test 2: Filtre 'video' retourne 2 items")

        # Test 3: Recherche
        filters_search = ContentFilter(search_query="Transcript")
        items, total = asyncio.run(get_content_items(test_db, filters_search))
        assert total == 1, f"Test 3 echoue: attendu 1, recu {total}"
        print("✓ Test 3: Recherche 'Transcript' retourne 1 item")

        print()
        print("="*60)
        print("TOUS LES TESTS PASSENT - Correction validee!")
        print("="*60)

    finally:
        os.unlink(test_db)


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
La variable 'where_clause' etait definie UNIQUEMENT dans le
bloc 'if where_conditions:'. Quand aucun filtre n'etait
applique, where_conditions etait une liste vide [], donc
le bloc if n'etait pas execute, et where_clause n'existait pas.

Plus tard, {where_clause} dans le f-string causait un NameError
qui etait capture silencieusement par le try/except.

CODE BUGGY:
-----------
    where_conditions = []
    params = []

    if where_conditions:  # False si liste vide
        where_clause = " WHERE ..."  # Jamais execute!

    ... {where_clause} ...  # NameError!

CODE CORRIGE:
-------------
    where_clause = ""  # <-- AJOUTE
    where_conditions = []
    params = []

    if where_conditions:
        where_clause = " WHERE ..."

    ... {where_clause} ...  # OK, vaut "" ou " WHERE ..."

LECON:
------
Toujours initialiser une variable AVANT un bloc conditionnel
si elle est utilisee APRES ce bloc.
============================================================
""")


if __name__ == "__main__":
    run_tests()
    print()
    show_explanation()
