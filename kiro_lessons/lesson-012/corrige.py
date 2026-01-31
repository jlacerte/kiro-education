"""
Cours 012: CSS Input - Textarea Multi-ligne
===========================================
CORRIGE - Solution Complete

Ce fichier montre l'input CORRIGE avec textarea multi-ligne.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass
from typing import List


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class InputConfig:
    """Configuration d'un champ de saisie."""
    element_type: str
    max_visible_chars: int
    supports_newlines: bool
    rows: int = 1
    min_height: int = 60
    max_height: int = 150


@dataclass
class UserMessage:
    """Un message utilisateur."""
    text: str
    line_count: int
    visible: bool


# ============================================================================
# SOLUTION: TEXTAREA MULTI-LIGNE
# ============================================================================

class ChatTextarea:
    """Champ de saisie multi-ligne corrige."""

    def __init__(self):
        # =============================================
        # CORRECTION: Textarea multi-ligne!
        # =============================================
        self.config = InputConfig(
            element_type="textarea",
            max_visible_chars=150,  # 50 chars x 3 lignes
            supports_newlines=True,
            rows=3,
            min_height=60,
            max_height=150
        )

    def process_message(self, text: str) -> UserMessage:
        """Traite un message entrant."""
        line_count = text.count('\n') + 1

        return UserMessage(
            text=text,
            line_count=line_count,
            visible=True  # Tout est visible avec le scroll
        )

    def render_html(self) -> str:
        """Genere le HTML du textarea."""
        return f'''<div class="chat-input-container">
    <div class="input-wrapper">
        <textarea
            class="chat-textarea"
            rows="{self.config.rows}"
            placeholder="Type your message... (Shift+Enter for new line)"
        ></textarea>
        <button class="send-button">Send</button>
    </div>
</div>'''

    def render_css(self) -> str:
        """Genere le CSS du textarea."""
        return f'''.chat-input-container {{
    padding: 10px;
    background: #1a1a2e;
    border-top: 1px solid #00ff41;
}}

.input-wrapper {{
    display: flex;
    gap: 10px;
    align-items: flex-end;
}}

.chat-textarea {{
    flex: 1;
    min-height: {self.config.min_height}px;
    max-height: {self.config.max_height}px;
    padding: 10px;
    border: 1px solid #00ff41;
    border-radius: 4px;
    background: #0a0a14;
    color: #00ff41;
    font-family: monospace;
    font-size: 14px;
    resize: vertical;
    line-height: 1.4;
}}

.chat-textarea:focus {{
    outline: none;
    border-color: #00ff88;
    box-shadow: 0 0 5px rgba(0, 255, 65, 0.3);
}}

.send-button {{
    padding: 10px 20px;
    height: 40px;
    background: #00ff41;
    color: #0a0a14;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}}'''

    def render_js(self) -> str:
        """Genere le JavaScript pour Enter/Shift+Enter."""
        return '''const textarea = document.querySelector('.chat-textarea');

textarea.addEventListener('keydown', (e) => {
    // Enter sans Shift = envoyer
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
    // Shift+Enter = nouvelle ligne (comportement par defaut)
});

function sendMessage() {
    const text = textarea.value.trim();
    if (text) {
        // Envoyer le message
        console.log('Sending:', text);
        textarea.value = '';
    }
}'''


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
# VERIFICATION
# ============================================================================

def run_tests():
    """Execute les tests du textarea corrige."""

    print("=" * 60)
    print("COURS 012 - CORRIGE - Textarea Multi-ligne")
    print("=" * 60)
    print()

    textarea = ChatTextarea()

    print("Configuration corrigee:")
    print("-" * 40)
    print(f"  Element: <{textarea.config.element_type}>")
    print(f"  Lignes: {textarea.config.rows}")
    print(f"  Retours a la ligne: Oui")
    print(f"  Hauteur: {textarea.config.min_height}-{textarea.config.max_height}px")
    print(f"  Redimensionnement: vertical")
    print()

    print("Test avec differents messages:")
    print("-" * 40)

    for i, msg in enumerate(TEST_MESSAGES, 1):
        result = textarea.process_message(msg)

        print(f"\n  Message {i}:")
        print(f"  Longueur: {len(result.text)} caracteres")
        print(f"  Lignes: {result.line_count}")
        print(f"  Status: [OK] Tout visible")

    print()
    print("=" * 60)
    print("TOUS LES MESSAGES SONT VISIBLES!")
    return True


def show_code():
    """Affiche le code de la solution."""

    textarea = ChatTextarea()

    print("""
============================================================
CODE DE LA SOLUTION
============================================================
""")

    print("HTML:")
    print("-" * 40)
    print(textarea.render_html())
    print()

    print("CSS:")
    print("-" * 40)
    print(textarea.render_css())
    print()

    print("JavaScript:")
    print("-" * 40)
    print(textarea.render_js())


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
<input type="text"> ne permet qu'une seule ligne.
Les messages longs sont tronques visuellement.
Impossible de coller du code formate.

CORRECTION:
-----------
Remplacer par <textarea rows="3">:
- Plusieurs lignes visibles
- Retours a la ligne supportes
- Redimensionnable par l'utilisateur

PROPRIETES CSS IMPORTANTES:
---------------------------
resize: vertical;     /* Seulement vertical */
min-height: 60px;     /* Au moins 3 lignes */
max-height: 150px;    /* Limite pour ne pas envahir */

GESTION CLAVIER:
----------------
- Enter: Envoyer le message
- Shift+Enter: Nouvelle ligne

Le comportement par defaut de textarea est "Enter = nouvelle ligne".
On intercepte Enter pour envoyer, sauf si Shift est presse.

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_code()
    print()
    show_explanation()
