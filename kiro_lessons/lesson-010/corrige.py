"""
Cours 010: Recherche Multi-Sources (KB + Index Video)
=====================================================
CORRIGE - Solution Complete

Ce fichier montre la solution CORRIGEE.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class Video:
    """Represente une video YouTube."""
    video_id: str
    title: str
    channel: str
    description: str
    has_transcript: bool = False


@dataclass
class SearchResults:
    """Resultats de recherche."""
    kb_results: List[Video]
    suggestions: List[Video]


# ============================================================================
# SIMULATION DE LA BASE DE DONNEES
# ============================================================================

class KnowledgeBase:
    """Simule la Knowledge Base (videos avec transcripts)."""

    def __init__(self):
        self.videos: Dict[str, Video] = {}

    def add(self, video: Video):
        """Ajoute une video avec son transcript."""
        video.has_transcript = True
        self.videos[video.video_id] = video

    def search(self, query: str) -> List[Video]:
        """Recherche dans les transcripts existants."""
        query_lower = query.lower()
        keywords = query_lower.split()

        results = []
        for video in self.videos.values():
            text = f"{video.title} {video.description}".lower()
            if any(kw in text for kw in keywords):
                results.append(video)

        return results


class VideoIndex:
    """Simule l'index des videos YouTube (avec ou sans transcript)."""

    def __init__(self):
        self.videos: Dict[str, Video] = {}

    def add(self, video: Video):
        """Ajoute une video a l'index."""
        self.videos[video.video_id] = video

    def search(self, query: str) -> List[Video]:
        """Recherche dans l'index (FTS5 simule)."""
        query_lower = query.lower()
        keywords = query_lower.split()

        results = []
        for video in self.videos.values():
            text = f"{video.title} {video.description}".lower()
            if any(kw in text for kw in keywords):
                results.append(video)

        return results


# ============================================================================
# SERVICE DE CHAT CORRIGE
# ============================================================================

class ChatService:
    """Service de chat AI - VERSION CORRIGEE."""

    def __init__(self, kb: KnowledgeBase, video_index: VideoIndex):
        self.kb = kb
        self.video_index = video_index

    def search(self, query: str) -> SearchResults:
        """Recherche dans TOUTES les sources."""

        # =============================================
        # CORRECTION: Recherche multi-sources
        # =============================================

        # 1. Chercher dans la KB (transcripts existants)
        kb_results = self.kb.search(query)

        # 2. Chercher dans l'index video (NOUVEAU!)
        index_results = self.video_index.search(query)

        # 3. Filtrer les videos sans transcript
        #    (ne pas suggerer celles deja dans la KB)
        kb_video_ids = {v.video_id for v in kb_results}
        suggestions = [
            v for v in index_results
            if v.video_id not in kb_video_ids  # Pas deja dans les resultats
            and not v.has_transcript  # Pas encore de transcript
        ]

        return SearchResults(
            kb_results=kb_results,
            suggestions=suggestions
        )

    def generate_response(self, query: str) -> str:
        """Genere une reponse pour l'utilisateur."""
        results = self.search(query)

        response_parts = []

        # Partie 1: Reponse basee sur la KB
        if results.kb_results:
            response_parts.append("Based on the transcripts I have:\n")
            for video in results.kb_results[:3]:
                response_parts.append(f"  - {video.title} by {video.channel}")
        else:
            response_parts.append("I don't have any transcripts matching your query.")

        # Partie 2: Suggestions (maintenant fonctionnel!)
        if results.suggestions:
            response_parts.append("\n\nRelated videos available for download:")
            for video in results.suggestions[:5]:
                response_parts.append(f"  [{video.title}] [Download]")

        return "\n".join(response_parts)


# ============================================================================
# DONNEES DE TEST
# ============================================================================

def setup_test_data() -> tuple:
    """Configure les donnees de test."""

    kb = KnowledgeBase()
    video_index = VideoIndex()

    # Videos AVEC transcript (dans la KB)
    kb.add(Video(
        video_id="vid_001",
        title="The Simplest RAG Stack",
        channel="Cole Medin",
        description="Build a hybrid search RAG agent with MongoDB"
    ))

    kb.add(Video(
        video_id="vid_002",
        title="Python FastAPI Tutorial",
        channel="Tech Channel",
        description="Complete guide to building APIs with FastAPI"
    ))

    # Videos dans l'index (avec ou sans transcript)
    video_index.add(Video(
        video_id="vid_001",
        title="The Simplest RAG Stack",
        channel="Cole Medin",
        description="Build a hybrid search RAG agent",
        has_transcript=True
    ))

    video_index.add(Video(
        video_id="vid_003",
        title="Build a RAG AI Agent from Scratch",
        channel="Cole Medin",
        description="Step by step RAG implementation tutorial",
        has_transcript=False
    ))

    video_index.add(Video(
        video_id="vid_004",
        title="RAG Best Practices 2024",
        channel="AI Weekly",
        description="Top 10 tips for production RAG systems",
        has_transcript=False
    ))

    video_index.add(Video(
        video_id="vid_005",
        title="Advanced RAG Techniques",
        channel="Cole Medin",
        description="Hybrid search, reranking, and more",
        has_transcript=False
    ))

    video_index.add(Video(
        video_id="vid_006",
        title="Machine Learning Basics",
        channel="ML Academy",
        description="Introduction to machine learning concepts",
        has_transcript=False
    ))

    return kb, video_index


# ============================================================================
# VERIFICATION
# ============================================================================

def run_tests():
    """Execute les tests corriges."""

    print("=" * 60)
    print("COURS 010 - CORRIGE - Recherche Multi-Sources")
    print("=" * 60)
    print()

    kb, video_index = setup_test_data()
    chat = ChatService(kb, video_index)

    # Test de recherche
    query = "RAG"

    print(f"User Query: '{query}'")
    print("-" * 40)
    print()

    # Effectuer la recherche
    results = chat.search(query)

    print("Resultats de la recherche:")
    print("-" * 40)
    print(f"  KB results: {len(results.kb_results)}")
    for v in results.kb_results:
        print(f"    - {v.title} [transcript disponible]")

    print(f"\n  Suggestions: {len(results.suggestions)}")
    for v in results.suggestions:
        print(f"    - {v.title} [download disponible]")

    print()

    # Generer la reponse
    print("Reponse du chat:")
    print("-" * 40)
    response = chat.generate_response(query)
    print(response)
    print()

    # Verifier le succes
    print("=" * 60)

    rag_videos_no_transcript = [
        v for v in video_index.videos.values()
        if "rag" in v.title.lower() and not v.has_transcript
    ]

    if len(results.suggestions) >= len(rag_videos_no_transcript):
        print("RECHERCHE MULTI-SOURCES FONCTIONNELLE!")
        print(f"  {len(results.suggestions)} suggestions proposees")
        return True
    else:
        print("ERREUR: Suggestions manquantes")
        return False


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Le chat cherchait SEULEMENT dans la Knowledge Base.
Les videos sans transcript etaient ignorees.

CORRECTION:
-----------
Chercher dans DEUX sources:
1. KB (transcripts) -> Reponse AI detaillee
2. video_index (toutes les videos) -> Suggestions

def search(self, query: str) -> SearchResults:
    # 1. Chercher dans la KB
    kb_results = self.kb.search(query)

    # 2. Chercher dans l'index video (NOUVEAU!)
    index_results = self.video_index.search(query)

    # 3. Filtrer les suggestions
    kb_video_ids = {v.video_id for v in kb_results}
    suggestions = [
        v for v in index_results
        if v.video_id not in kb_video_ids
        and not v.has_transcript
    ]

    return SearchResults(kb_results, suggestions)

============================================================
""")


def show_workflow():
    """Affiche le workflow complet."""
    print("""
============================================================
WORKFLOW UTILISATEUR
============================================================

1. USER: "What videos about RAG?"
         |
         v
2. CHAT cherche dans:
   - KB (transcripts existants)
   - video_index (toutes les videos)
         |
         v
3. REPONSE:
   "Based on transcripts I have:
     - The Simplest RAG Stack by Cole Medin

    Related videos available for download:
     [Build a RAG AI Agent] [Download]
     [RAG Best Practices 2024] [Download]
     [Advanced RAG Techniques] [Download]"
         |
         v
4. USER clique [Download]
         |
         v
5. SYSTEME:
   - Telecharge le transcript
   - Ajoute a la KB
   - Affiche "Downloaded! [View in KB]"

============================================================
""")


def show_pattern():
    """Affiche le pattern de recherche federee."""
    print("""
============================================================
PATTERN: RECHERCHE FEDEREE
============================================================

class FederatedSearch:
    def __init__(self, sources: List[SearchSource]):
        self.sources = sources

    async def search(self, query: str) -> List[Result]:
        # Chercher dans toutes les sources en parallele
        tasks = [s.search(query) for s in self.sources]
        all_results = await asyncio.gather(*tasks)

        # Combiner et dedupliquer
        combined = []
        seen = set()
        for results in all_results:
            for result in results:
                if result.id not in seen:
                    combined.append(result)
                    seen.add(result.id)

        # Trier par pertinence
        return sorted(combined, key=lambda r: r.score, reverse=True)

AVANTAGES:
----------
- Recherche parallele (rapide)
- Resultats dedupliques
- Extensible (ajouter des sources facilement)

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_explanation()
    show_workflow()
    show_pattern()
