"""
Cours 012: CSS Input - Textarea Multi-ligne
===========================================
EXERCICE - Code a corriger

Niveau: Debutant
Duree: 15-20 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un input single-line problematique
2. Lance le script pour voir les limitations
3. Remplace par un textarea multi-ligne
4. Gere Enter vs Shift+Enter

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass
from typing import List


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class InputConfig:
    """Configuration d'un champ de saisie."""
    element_type: str  # "input" ou "textarea"
    max_visible_chars: int
    supports_newlines: bool
    rows: int = 1


@dataclass
class UserMessage:
    """Un message utilisateur."""
    text: str
    truncated: bool
    visible_text: str


# ============================================================================
# SIMULATION D'INPUT SINGLE-LINE - A CORRIGER
# ============================================================================

class ChatInput:
    """Simule un champ de saisie de chat."""

    def __init__(self):
        # =============================================
        # BUG: Input single-line!
        # - Texte long tronque visuellement
        # - Pas de retour a la ligne possible
        # =============================================
        self.config = InputConfig(
            element_type="input",
            max_visible_chars=50,  # Largeur typique d'un input
            supports_newlines=False,
            rows=1
        )

    def process_message(self, text: str) -> UserMessage:
        """Traite un message entrant."""
        # Supprimer les retours a la ligne (input ne les supporte pas)
        if not self.config.supports_newlines:
            text = text.replace('\n', ' ')

        # Calculer ce qui est visible
        visible = text[-self.config.max_visible_chars:]
        truncated = len(text) > self.config.max_visible_chars

        return UserMessage(
            text=text,
            truncated=truncated,
            visible_text=visible
        )

    def render_html(self) -> str:
        """Genere le HTML du champ de saisie."""
        if self.config.element_type == "input":
            return '<input type="text" placeholder="Type your message...">'
        else:
            return f'<textarea rows="{self.config.rows}" placeholder="Type your message..."></textarea>'


# ============================================================================
# MESSAGES DE TEST
# ============================================================================

TEST_MESSAGES = [
    "Hi there!",
    "Can you explain how RAG works?",
    "Can you explain RAG architecture, including embeddings, vector databases, and how do I implement hybrid search with reranking?",
    """Here's my code that doesn't work:
def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

What's wrong?""",
]


# ============================================================================
# ANALYSE ET VERIFICATION
# ============================================================================

def analyze_input():
    """Analyse les limitations de l'input single-line."""

    print("=" * 60)
    print("COURS 012 - Textarea Multi-ligne")
    print("=" * 60)
    print()

    chat_input = ChatInput()

    print("Configuration actuelle:")
    print("-" * 40)
    print(f"  Element: <{chat_input.config.element_type}>")
    print(f"  Caracteres visibles: {chat_input.config.max_visible_chars}")
    print(f"  Retours a la ligne: {'Oui' if chat_input.config.supports_newlines else 'Non'}")
    print(f"  Lignes: {chat_input.config.rows}")
    print()

    print("HTML genere:")
    print("-" * 40)
    print(f"  {chat_input.render_html()}")
    print()

    print("Test avec differents messages:")
    print("-" * 40)

    problems = []

    for i, msg in enumerate(TEST_MESSAGES, 1):
        result = chat_input.process_message(msg)

        print(f"\n  Message {i}:")
        print(f"  Longueur: {len(result.text)} caracteres")

        if result.truncated:
            print(f"  [TRONQUE] Visible: '...{result.visible_text}'")
            problems.append(f"Message {i} tronque")
        else:
            print(f"  [OK] Visible: '{result.visible_text}'")

        if '\n' in msg and not chat_input.config.supports_newlines:
            print(f"  [PROBLEME] Retours a la ligne supprimes!")
            problems.append(f"Message {i} perd ses retours a la ligne")

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
  Remplacer <input> par <textarea>:

  HTML:
  -----
  <textarea
      class="chat-textarea"
      rows="3"
      placeholder="Type your message..."
  ></textarea>

  CSS:
  ----
  .chat-textarea {
      min-height: 60px;
      max-height: 150px;
      resize: vertical;
  }

  JavaScript (Enter vs Shift+Enter):
  ----------------------------------
  textarea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
      }
  });
""")
        return False
    else:
        print("AUCUN PROBLEME!")
        return True


def show_comparison():
    """Montre la comparaison visuelle."""
    print("""
============================================================
COMPARAISON VISUELLE
============================================================

INPUT SINGLE-LINE (problematique):
┌────────────────────────────────────────────────┐
│ ...how do I implement hybrid search with reran │  <- tronque!
└────────────────────────────────────────────────┘
  ^ L'utilisateur ne voit pas le debut de sa question

TEXTAREA MULTI-LIGNE (solution):
┌────────────────────────────────────────────────┐
│ Can you explain RAG architecture, including    │
│ embeddings, vector databases, and how do I     │
│ implement hybrid search with reranking?        │
└────────────────────────────────────────────────┘
  ^ Tout le texte est visible!

AVANTAGES DU TEXTAREA:
- Voir tout le message
- Retours a la ligne possibles
- Coller du code formate
- Redimensionnable par l'utilisateur

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_input()
    print()
    show_comparison()
