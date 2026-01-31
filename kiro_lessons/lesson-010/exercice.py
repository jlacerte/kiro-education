"""
Cours 010: Recherche Multi-Sources (KB + Index Video)
=====================================================
EXERCICE - Code a corriger

Niveau: Intermediaire
Duree: 35-45 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un chat qui cherche SEULEMENT dans la KB
2. Lance le script pour voir le probleme
3. Ajoute la recherche dans l'index video
4. Les suggestions doivent apparaitre

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import re


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
# SERVICE DE CHAT AVEC BUG - A CORRIGER
# ============================================================================

class ChatService:
    """Service de chat AI."""

    def __init__(self, kb: KnowledgeBase, video_index: VideoIndex):
        self.kb = kb
        self.video_index = video_index

    def search(self, query: str) -> SearchResults:
        """Recherche pour repondre a une question."""

        # =============================================
        # BUG: Cherche SEULEMENT dans la KB!
        # Les videos sans transcript sont IGNOREES
        # =============================================
        kb_results = self.kb.search(query)

        # TODO: Ajouter la recherche dans video_index
        # suggestions = ???
        suggestions = []  # Toujours vide!

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

        # Partie 2: Suggestions (toujours vide a cause du bug!)
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

    # Videos SANS transcript (seulement dans l'index)
    # Ces videos devraient apparaitre comme suggestions!
    video_index.add(Video(
        video_id="vid_001",
        title="The Simplest RAG Stack",
        channel="Cole Medin",
        description="Build a hybrid search RAG agent",
        has_transcript=True  # Deja dans KB
    ))

    video_index.add(Video(
        video_id="vid_003",
        title="Build a RAG AI Agent from Scratch",
        channel="Cole Medin",
        description="Step by step RAG implementation tutorial",
        has_transcript=False  # PAS dans KB!
    ))

    video_index.add(Video(
        video_id="vid_004",
        title="RAG Best Practices 2024",
        channel="AI Weekly",
        description="Top 10 tips for production RAG systems",
        has_transcript=False  # PAS dans KB!
    ))

    video_index.add(Video(
        video_id="vid_005",
        title="Advanced RAG Techniques",
        channel="Cole Medin",
        description="Hybrid search, reranking, and more",
        has_transcript=False  # PAS dans KB!
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
# ANALYSE ET VERIFICATION
# ============================================================================

def analyze_bug():
    """Analyse le bug et montre le probleme."""

    print("=" * 60)
    print("COURS 010 - Recherche Multi-Sources")
    print("=" * 60)
    print()

    kb, video_index = setup_test_data()
    chat = ChatService(kb, video_index)

    # Test de recherche
    query = "RAG"

    print(f"User Query: '{query}'")
    print("-" * 40)
    print()

    # Afficher ce qui est disponible
    print("Donnees disponibles:")
    print("-" * 40)
    print(f"  KB (avec transcripts): {len(kb.videos)} videos")
    for v in kb.videos.values():
        print(f"    - {v.title}")

    print()
    print(f"  Index (toutes les videos): {len(video_index.videos)} videos")
    for v in video_index.videos.values():
        status = "[KB]" if v.has_transcript else "[No transcript]"
        print(f"    - {v.title} {status}")

    print()

    # Effectuer la recherche
    results = chat.search(query)

    print("Resultats de la recherche:")
    print("-" * 40)
    print(f"  KB results: {len(results.kb_results)}")
    print(f"  Suggestions: {len(results.suggestions)}")
    print()

    # Generer la reponse
    print("Reponse du chat:")
    print("-" * 40)
    response = chat.generate_response(query)
    print(response)
    print()

    # Verifier le bug
    print("=" * 60)

    # Combien de videos RAG sans transcript?
    rag_videos_no_transcript = [
        v for v in video_index.videos.values()
        if "rag" in v.title.lower() and not v.has_transcript
    ]

    if len(results.suggestions) == 0 and len(rag_videos_no_transcript) > 0:
        print("BUG DETECTE!")
        print("-" * 40)
        print()
        print(f"  Il y a {len(rag_videos_no_transcript)} video(s) sur RAG")
        print("  qui ne sont pas proposees a l'utilisateur:")
        for v in rag_videos_no_transcript:
            print(f"    - {v.title}")
        print()
        print("PROBLEME:")
        print("  Le chat cherche SEULEMENT dans la KB.")
        print("  Les videos sans transcript sont ignorees.")
        print()
        print("SOLUTION:")
        print("-" * 40)
        print("""
  Dans ChatService.search():

  def search(self, query: str) -> SearchResults:
      # 1. Chercher dans la KB
      kb_results = self.kb.search(query)

      # 2. Chercher dans l'index video
      index_results = self.video_index.search(query)

      # 3. Filtrer les videos sans transcript (pas dans KB)
      kb_ids = {v.video_id for v in kb_results}
      suggestions = [
          v for v in index_results
          if v.video_id not in kb_ids
          and not v.has_transcript
      ]

      return SearchResults(
          kb_results=kb_results,
          suggestions=suggestions
      )
""")
        return False
    else:
        print("RECHERCHE MULTI-SOURCES FONCTIONNELLE!")
        return True


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_bug()
