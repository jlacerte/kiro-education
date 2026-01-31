"""
Cours 013: CSS Position Fixed - Elements UI Persistants
=======================================================
EXERCICE - Code a corriger

Niveau: Intermediaire
Duree: 30-40 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un layout ou les elements disparaissent au scroll
2. Lance le script pour voir le probleme
3. Applique position: fixed aux elements qui doivent rester visibles
4. N'oublie pas le margin-bottom pour le contenu!

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

class Position(Enum):
    STATIC = "static"
    RELATIVE = "relative"
    ABSOLUTE = "absolute"
    FIXED = "fixed"
    STICKY = "sticky"


@dataclass
class UIElement:
    """Un element UI avec sa position."""
    name: str
    position: Position
    top: int | None = None
    bottom: int | None = None
    height: int = 30
    z_index: int = 0


@dataclass
class ViewportState:
    """Etat du viewport apres scroll."""
    scroll_y: int
    visible_elements: List[str]
    hidden_elements: List[str]


# ============================================================================
# LAYOUT AVEC ELEMENTS QUI DISPARAISSENT - A CORRIGER
# ============================================================================

class ChatLayout:
    """Simule un layout de chat."""

    def __init__(self):
        self.viewport_height = 600
        self.content_height = 1500  # Beaucoup de messages

        # =============================================
        # BUG: Elements en position static!
        # Ils vont disparaitre au scroll
        # =============================================
        self.elements: List[UIElement] = [
            UIElement(
                name="Header",
                position=Position.FIXED,  # Celui-ci est OK
                top=0,
                height=50,
                z_index=1000
            ),
            UIElement(
                name="Messages",
                position=Position.STATIC,  # Normal
                height=self.content_height
            ),
            UIElement(
                name="Input",
                position=Position.STATIC,  # BUG: Devrait etre fixed!
                bottom=30,
                height=60
            ),
            UIElement(
                name="Status Bar",
                position=Position.STATIC,  # BUG: Devrait etre fixed!
                bottom=0,
                height=28
            ),
        ]

        self.content_margin_bottom = 0  # BUG: Devrait etre ~100px

    def simulate_scroll(self, scroll_y: int) -> ViewportState:
        """Simule le scroll et retourne l'etat de visibilite."""
        visible = []
        hidden = []

        for el in self.elements:
            is_visible = self._is_visible(el, scroll_y)
            if is_visible:
                visible.append(el.name)
            else:
                hidden.append(el.name)

        return ViewportState(
            scroll_y=scroll_y,
            visible_elements=visible,
            hidden_elements=hidden
        )

    def _is_visible(self, element: UIElement, scroll_y: int) -> bool:
        """Determine si un element est visible apres scroll."""

        # Fixed: toujours visible
        if element.position == Position.FIXED:
            return True

        # Static/Relative: depend du scroll
        if element.position in (Position.STATIC, Position.RELATIVE):
            # Elements en bas de page disparaissent si on scroll vers le haut
            if element.bottom is not None:
                # Element positionne en bas
                element_top = self.content_height - element.bottom - element.height
                return element_top < (scroll_y + self.viewport_height)

        return True  # Par defaut visible


# ============================================================================
# ANALYSE ET VERIFICATION
# ============================================================================

def analyze_layout():
    """Analyse le layout et montre les problemes."""

    print("=" * 60)
    print("COURS 013 - Position Fixed UI")
    print("=" * 60)
    print()

    layout = ChatLayout()

    print("Elements du layout:")
    print("-" * 40)

    for el in layout.elements:
        pos_status = "[OK]" if el.position == Position.FIXED else "[ATTENTION]"
        print(f"\n  {el.name} {pos_status}")
        print(f"    position: {el.position.value}")
        print(f"    height: {el.height}px")
        if el.z_index:
            print(f"    z-index: {el.z_index}")

    print()
    print(f"  content margin-bottom: {layout.content_margin_bottom}px")
    print()

    # Simuler differentes positions de scroll
    scroll_tests = [0, 300, 600, 1000]

    print("Simulation du scroll:")
    print("-" * 40)

    problems = []

    for scroll_y in scroll_tests:
        state = layout.simulate_scroll(scroll_y)
        print(f"\n  scroll_y = {scroll_y}px")
        print(f"    Visible: {', '.join(state.visible_elements)}")

        if state.hidden_elements:
            print(f"    CACHE: {', '.join(state.hidden_elements)}")
            for hidden in state.hidden_elements:
                if hidden in ("Input", "Status Bar"):
                    problems.append(f"{hidden} cache a scroll_y={scroll_y}")

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
  1. Appliquer position: fixed aux elements persistants:

     .mc-status-bar {
         position: fixed;
         bottom: 0;
         left: 0;
         right: 0;
         z-index: 1000;
     }

     .chat-input-container {
         position: fixed;
         bottom: 30px;  /* Au-dessus de status bar */
         left: 200px;   /* Apres sidebar */
         right: 0;
         z-index: 999;
     }

  2. Ajouter margin-bottom au contenu:

     .message-area {
         margin-bottom: 100px;  /* Input + Status */
     }
""")
        return False
    else:
        print("TOUS LES ELEMENTS RESTENT VISIBLES!")
        return True


def show_visualization():
    """Montre une visualisation du probleme."""
    print("""
============================================================
VISUALISATION DU PROBLEME
============================================================

SCROLL = 0 (en bas):
┌────────────────────────────────────────┐
│  Header (fixed)                    OK  │
├────────────────────────────────────────┤
│  Message 8                             │
│  Message 9                             │
│  Message 10                            │
├────────────────────────────────────────┤
│  [Input________________________]   OK  │
├────────────────────────────────────────┤
│  ● SYSTEM: ONLINE                  OK  │
└────────────────────────────────────────┘

SCROLL = 1000 (vers le haut):
┌────────────────────────────────────────┐
│  Header (fixed)                    OK  │
├────────────────────────────────────────┤
│  Message 1                             │
│  Message 2                             │
│  Message 3                             │
│  Message 4                             │
│  Message 5                             │
└────────────────────────────────────────┘
  Input: DISPARU!
  Status: DISPARU!

L'utilisateur ne peut plus envoyer de message!

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_layout()
    print()
    show_visualization()
