"""
Cours 014: Pattern - Detection de Workflow par Intention
========================================================
EXERCICE - Code a corriger

Niveau: Avance
Duree: 40-50 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un chat SANS detection de workflow
2. Lance le script pour voir le probleme
3. Implemente la detection d'intention
4. Ajoute les marqueurs de workflow

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class ChatMessage:
    """Un message de chat."""
    role: str  # "user" ou "assistant"
    content: str
    workflow: int = 0


@dataclass
class WorkflowConfig:
    """Configuration d'un workflow."""
    id: int
    name: str
    patterns: List[str]
    prompt: str


# ============================================================================
# CHAT SANS DETECTION DE WORKFLOW - A CORRIGER
# ============================================================================

class SimpleChatService:
    """Service de chat SANS detection de workflow."""

    def __init__(self):
        self.history: List[ChatMessage] = []

        # =============================================
        # BUG: Pas de detection de workflow!
        # Toutes les questions ont la meme reponse generique
        # =============================================
        self.default_prompt = "Tu es un assistant generique."

    def process(self, user_message: str) -> str:
        """Traite un message utilisateur."""
        self.history.append(ChatMessage(role="user", content=user_message))

        # BUG: Toujours la meme reponse generique!
        response = self._generate_generic_response(user_message)

        self.history.append(ChatMessage(role="assistant", content=response))

        return response

    def _generate_generic_response(self, message: str) -> str:
        """Genere une reponse generique (pas contextuelle)."""
        return f"Je peux vous aider avec ca. Votre question etait: '{message[:50]}...'"


# ============================================================================
# MESSAGES DE TEST
# ============================================================================

TEST_MESSAGES = [
    ("What videos do you have about RAG?", 1),  # WF1 - Videos
    ("Show me the artifacts from that video", 2),  # WF2 - Artifacts
    ("What did Cole say about vector databases?", 3),  # WF3 - RAG/KB
    ("Generate a summary of this transcript", 4),  # WF4 - Generate
    ("How are you today?", 0),  # Pas de workflow
]


# ============================================================================
# ANALYSE ET VERIFICATION
# ============================================================================

def analyze_chat():
    """Analyse le chat et montre les problemes."""

    print("=" * 60)
    print("COURS 014 - Workflow Detection Pattern")
    print("=" * 60)
    print()

    chat = SimpleChatService()

    print("Test du chat SANS detection de workflow:")
    print("-" * 40)

    problems = []

    for message, expected_wf in TEST_MESSAGES:
        response = chat.process(message)

        print(f"\n  User: {message[:50]}...")
        print(f"  Expected WF: {expected_wf}")
        print(f"  AI: {response[:60]}...")

        # Verifier si le workflow est detecte
        if expected_wf > 0:
            # La reponse devrait etre specifique au workflow
            if "generique" in response.lower() or "votre question" in response.lower():
                problems.append(f"WF{expected_wf} non detecte: '{message[:30]}...'")

    print()
    print("=" * 60)

    if problems:
        print("PROBLEMES DETECTES!")
        print("-" * 40)
        for p in problems:
            print(f"  - {p}")
        print()
        print("SOLUTION:")
        print("-" * 40)
        print("""
  1. Definir les patterns pour chaque workflow:

     WORKFLOW_PATTERNS = {
         1: ['video', 'videos', 'watch', 'youtube'],
         2: ['artifact', 'transcript', 'summary'],
         3: ['what did', 'search', 'find info', 'rag'],
         4: ['generate', 'create', 'make'],
     }

  2. Implementer la detection:

     def detect_workflow(message: str) -> int:
         message_lower = message.lower()
         for wf_num, patterns in WORKFLOW_PATTERNS.items():
             if any(p in message_lower for p in patterns):
                 return wf_num
         return 0

  3. Charger le prompt specifique:

     def get_workflow_prompt(wf_num: int) -> str:
         path = f"config/workflows/wf{wf_num}.md"
         return Path(path).read_text()

  4. Ajouter le marqueur dans la reponse:

     response += f'<span data-wf="{wf_num}"></span>'
""")
        return False
    else:
        print("DETECTION DE WORKFLOW FONCTIONNELLE!")
        return True


def show_expected_behavior():
    """Montre le comportement attendu."""
    print("""
============================================================
COMPORTEMENT ATTENDU
============================================================

AVANT (Sans detection):
-----------------------
User: "What videos about RAG?"
AI: "Je peux vous aider avec ca. Votre question etait..."
    [Reponse generique - PAS UTILE]

APRES (Avec detection):
-----------------------
User: "What videos about RAG?"
AI: [WF1 Active]
    "I found 3 videos about RAG:
     - RAG Tutorial by Cole Medin [Download]
     - Building RAG Systems [Download]
     - Advanced RAG Techniques [Download]"
    [Reponse specifique au workflow VIDEO]

WORKFLOW DETECTES:
------------------
WF1 - Videos:    "video", "youtube", "watch"
WF2 - Artifacts: "artifact", "summary", "transcript"
WF3 - RAG/KB:    "what did", "search", "find info"
WF4 - Generate:  "generate", "create", "make"
WF5 - Export:    "export", "download", "share"

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_chat()
    print()
    show_expected_behavior()
