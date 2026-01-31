"""
Cours 014: Pattern - Detection de Workflow par Intention
========================================================
CORRIGE - Solution Complete

Ce fichier montre le chat CORRIGE avec detection de workflow.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class ChatMessage:
    """Un message de chat."""
    role: str
    content: str
    workflow: int = 0


@dataclass
class WorkflowResponse:
    """Reponse avec workflow detecte."""
    content: str
    workflow: int
    marker: str


# ============================================================================
# CONFIGURATION DES WORKFLOWS
# ============================================================================

WORKFLOW_PATTERNS: Dict[int, List[str]] = {
    1: ['video', 'videos', 'watch', 'youtube', 'channel'],
    2: ['artifact', 'transcript', 'summary', 'notes', 'document'],
    3: ['what did', 'search kb', 'find info', 'knowledge', 'rag'],
    4: ['generate', 'create', 'make', 'produce'],
    5: ['export', 'download', 'share', 'save'],
}

WORKFLOW_NAMES: Dict[int, str] = {
    0: "General",
    1: "Videos",
    2: "Artifacts",
    3: "RAG/KB",
    4: "Generate",
    5: "Export",
}

# Prompts simules (normalement dans des fichiers MD)
WORKFLOW_PROMPTS: Dict[int, str] = {
    1: """Tu es un assistant specialise dans la recherche de videos YouTube.
Quand l'utilisateur cherche des videos:
- Liste les videos trouvees avec titre et channel
- Propose des boutons Download pour les videos sans transcript
- Format compact et actionnable""",

    2: """Tu es un assistant qui gere les artefacts (summaries, FAQs, transcripts).
Quand l'utilisateur demande des artefacts:
- Liste les artefacts disponibles groupes par type
- Propose des actions (view, edit, export)
- Montre les metadonnees (date, source)""",

    3: """Tu es un assistant RAG qui recherche dans la Knowledge Base.
Quand l'utilisateur pose une question:
- Cherche dans les transcripts existants
- Cite les sources avec timestamps
- Reponds de maniere concise et factuelle""",

    4: """Tu es un assistant de generation de contenu.
Quand l'utilisateur demande de generer:
- Confirme le type de contenu (summary, FAQ, podcast)
- Demande la source si necessaire
- Lance la generation et montre le progres""",

    5: """Tu es un assistant d'export de donnees.
Quand l'utilisateur veut exporter:
- Liste les formats disponibles (MD, PDF, JSON)
- Propose les options de partage
- Genere le lien de telechargement""",
}


# ============================================================================
# SERVICE DE DETECTION DE WORKFLOW
# ============================================================================

class WorkflowService:
    """Service de detection et gestion des workflows."""

    def detect(self, message: str) -> int:
        """Detecte le workflow a partir du message."""
        message_lower = message.lower()

        for wf_num, patterns in WORKFLOW_PATTERNS.items():
            if any(pattern in message_lower for pattern in patterns):
                return wf_num

        return 0  # Pas de workflow specifique

    def get_prompt(self, wf_num: int) -> str:
        """Retourne le prompt du workflow."""
        return WORKFLOW_PROMPTS.get(wf_num, "Tu es un assistant helpful.")

    def get_name(self, wf_num: int) -> str:
        """Retourne le nom du workflow."""
        return WORKFLOW_NAMES.get(wf_num, "Unknown")

    def create_marker(self, wf_num: int) -> str:
        """Cree le marqueur HTML pour le frontend."""
        if wf_num > 0:
            return f'<span class="wf-marker" data-wf="{wf_num}" style="display:none"></span>'
        return ""


# ============================================================================
# CHAT AVEC DETECTION DE WORKFLOW
# ============================================================================

class SmartChatService:
    """Service de chat AVEC detection de workflow."""

    def __init__(self):
        self.history: List[ChatMessage] = []
        self.workflow_service = WorkflowService()
        self.current_workflow = 0

    def process(self, user_message: str) -> WorkflowResponse:
        """Traite un message avec detection de workflow."""

        # 1. Detecter le workflow
        wf_num = self.workflow_service.detect(user_message)
        self.current_workflow = wf_num

        # 2. Enregistrer le message
        self.history.append(ChatMessage(
            role="user",
            content=user_message,
            workflow=wf_num
        ))

        # 3. Generer la reponse contextuelle
        response = self._generate_contextual_response(user_message, wf_num)

        # 4. Ajouter le marqueur
        marker = self.workflow_service.create_marker(wf_num)

        # 5. Enregistrer la reponse
        self.history.append(ChatMessage(
            role="assistant",
            content=response,
            workflow=wf_num
        ))

        return WorkflowResponse(
            content=response,
            workflow=wf_num,
            marker=marker
        )

    def _generate_contextual_response(self, message: str, wf_num: int) -> str:
        """Genere une reponse contextuelle au workflow."""

        wf_name = self.workflow_service.get_name(wf_num)

        if wf_num == 1:  # Videos
            return f"""[WF1 - {wf_name}]
I found videos matching your query:

1. "RAG Tutorial" by Cole Medin
   [View] [Download Transcript]

2. "Building RAG Systems" by AI Weekly
   [View] [Download Transcript]

3. "Advanced RAG Techniques" by Tech Channel
   [View] [Download Transcript]"""

        elif wf_num == 2:  # Artifacts
            return f"""[WF2 - {wf_name}]
Here are your artifacts:

Summaries:
- RAG Tutorial Summary (2024-01-10)
- ML Basics Summary (2024-01-09)

FAQs:
- RAG FAQ (5 questions)

Transcripts:
- 3 transcripts available

[View All] [Export]"""

        elif wf_num == 3:  # RAG/KB
            return f"""[WF3 - {wf_name}]
Based on the Knowledge Base:

Cole mentioned vector databases in "RAG Tutorial" at 5:32:
"Vector databases are essential for storing embeddings.
I recommend starting with ChromaDB for prototyping..."

Sources:
- RAG Tutorial (5:32-6:15)
- Advanced RAG (12:00-12:45)"""

        elif wf_num == 4:  # Generate
            return f"""[WF4 - {wf_name}]
I can generate the following content:

1. Summary - Condensed version of a transcript
2. FAQ - Common questions and answers
3. Podcast - Audio version with AI voice

Which would you like to generate?
[Summary] [FAQ] [Podcast]"""

        elif wf_num == 5:  # Export
            return f"""[WF5 - {wf_name}]
Export options available:

Formats:
- Markdown (.md)
- PDF (.pdf)
- JSON (.json)

What would you like to export?
[Artifacts] [Transcripts] [All Data]"""

        else:  # General
            return f"""I'm here to help! You can:
- Search for videos (WF1)
- View artifacts (WF2)
- Ask questions about content (WF3)
- Generate summaries/FAQs (WF4)
- Export your data (WF5)

What would you like to do?"""


# ============================================================================
# MESSAGES DE TEST
# ============================================================================

TEST_MESSAGES = [
    ("What videos do you have about RAG?", 1),
    ("Show me the artifacts from that video", 2),
    ("What did Cole say about vector databases?", 3),
    ("Generate a summary of this transcript", 4),
    ("How are you today?", 0),
]


# ============================================================================
# VERIFICATION
# ============================================================================

def run_tests():
    """Execute les tests du chat avec workflow."""

    print("=" * 60)
    print("COURS 014 - CORRIGE - Workflow Detection")
    print("=" * 60)
    print()

    chat = SmartChatService()

    print("Test du chat AVEC detection de workflow:")
    print("-" * 40)

    results = []

    for message, expected_wf in TEST_MESSAGES:
        response = chat.process(message)

        detected = response.workflow
        match = detected == expected_wf

        print(f"\n  User: {message[:45]}...")
        print(f"  Detected WF: {detected} ({chat.workflow_service.get_name(detected)})")
        print(f"  Expected WF: {expected_wf}")
        print(f"  Match: {'OK' if match else 'ERREUR'}")

        if response.marker:
            print(f"  Marker: {response.marker[:50]}...")

        results.append(match)

    print()
    print("=" * 60)

    if all(results):
        print(f"TOUS LES WORKFLOWS DETECTES! ({sum(results)}/{len(results)})")
        return True
    else:
        print(f"ERREURS: {len(results) - sum(results)}/{len(results)}")
        return False


def show_sample_responses():
    """Montre des exemples de reponses par workflow."""

    print("""
============================================================
EXEMPLES DE REPONSES PAR WORKFLOW
============================================================
""")

    chat = SmartChatService()

    for message, expected_wf in TEST_MESSAGES[:4]:
        response = chat.process(message)
        wf_name = chat.workflow_service.get_name(response.workflow)

        print(f"USER: {message}")
        print(f"WORKFLOW: WF{response.workflow} - {wf_name}")
        print("-" * 40)
        print(response.content)
        print()
        print("=" * 60)
        print()


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Le chat repondait de maniere generique a toutes les questions.
Pas de distinction entre les differentes intentions utilisateur.

CORRECTION:
-----------
1. DETECTION PAR PATTERNS:
   Analyser le message pour identifier l'intention.

   def detect(message: str) -> int:
       for wf_num, patterns in WORKFLOW_PATTERNS.items():
           if any(p in message.lower() for p in patterns):
               return wf_num
       return 0

2. PROMPTS MODULAIRES:
   Un prompt different pour chaque workflow.
   Idealement dans des fichiers MD separes.

3. REPONSES CONTEXTUELLES:
   Generer une reponse adaptee au workflow detecte.

4. MARQUEUR FRONTEND:
   Ajouter un marqueur cache pour mettre a jour l'UI.

   <span data-wf="2" style="display:none"></span>

AVANTAGES:
----------
- Reponses pertinentes et actionnables
- Navigation guidee pour l'utilisateur
- Prompts faciles a modifier
- UI reactive (boutons WF actifs)

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_sample_responses()
    show_explanation()
