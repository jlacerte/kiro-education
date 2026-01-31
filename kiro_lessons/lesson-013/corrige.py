"""
Cours 013: CSS Position Fixed - Elements UI Persistants
=======================================================
CORRIGE - Solution Complete

Ce fichier montre le layout CORRIGE avec position fixed.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass
from typing import List
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
    left: int | None = None
    right: int | None = None
    height: int = 30
    z_index: int = 0


@dataclass
class ViewportState:
    """Etat du viewport apres scroll."""
    scroll_y: int
    visible_elements: List[str]


# ============================================================================
# LAYOUT CORRIGE - POSITION FIXED
# ============================================================================

class FixedLayout:
    """Layout corrige avec elements fixes."""

    def __init__(self):
        self.viewport_height = 600
        self.content_height = 1500
        self.sidebar_width = 200

        # =============================================
        # CORRECTION: Position fixed pour les elements persistants!
        # =============================================
        self.elements: List[UIElement] = [
            UIElement(
                name="Header",
                position=Position.FIXED,
                top=0,
                left=0,
                right=0,
                height=50,
                z_index=1000
            ),
            UIElement(
                name="Messages",
                position=Position.RELATIVE,
                height=self.content_height
            ),
            UIElement(
                name="Input",
                position=Position.FIXED,  # CORRIGE!
                bottom=30,  # Au-dessus de status bar
                left=self.sidebar_width,  # Apres sidebar
                right=0,
                height=60,
                z_index=999
            ),
            UIElement(
                name="Status Bar",
                position=Position.FIXED,  # CORRIGE!
                bottom=0,
                left=0,
                right=0,
                height=28,
                z_index=1000
            ),
        ]

        # CORRIGE: Espace pour les elements fixes
        self.content_margin_bottom = 100  # Input (60) + Status (28) + padding

    def simulate_scroll(self, scroll_y: int) -> ViewportState:
        """Simule le scroll - tous les elements fixed restent visibles."""
        visible = []

        for el in self.elements:
            # Avec position: fixed, TOUT reste visible
            if el.position == Position.FIXED:
                visible.append(f"{el.name} (fixed)")
            else:
                visible.append(el.name)

        return ViewportState(
            scroll_y=scroll_y,
            visible_elements=visible
        )

    def get_css(self) -> str:
        """Genere le CSS pour les elements fixes."""
        return """/* Status bar fixe en bas */
.mc-status-bar {
    position: fixed !important;
    bottom: 0 !important;
    left: 0;
    right: 0;
    height: 28px;
    z-index: 1000;
    background: linear-gradient(to bottom, #1a1a2e, #0f0f1a);
    border-top: 1px solid #00ff41;
}

/* Input fixe au-dessus de status bar */
.chat-input-container {
    position: fixed !important;
    bottom: 30px !important;
    left: 200px !important;  /* Largeur sidebar */
    right: 0 !important;
    z-index: 999;
    background: #1a1a2e;
    padding: 10px;
}

/* Espace pour les elements fixes */
.message-area {
    margin-bottom: 100px !important;
    overflow-y: auto;
}

/* Alternative: avec variables CSS */
:root {
    --sidebar-width: 200px;
    --status-height: 28px;
    --input-height: 60px;
}

.chat-input-container {
    left: var(--sidebar-width);
    bottom: calc(var(--status-height) + 2px);
}"""


# ============================================================================
# VERIFICATION
# ============================================================================

def run_tests():
    """Execute les tests du layout corrige."""

    print("=" * 60)
    print("COURS 013 - CORRIGE - Position Fixed UI")
    print("=" * 60)
    print()

    layout = FixedLayout()

    print("Elements du layout corrige:")
    print("-" * 40)

    for el in layout.elements:
        print(f"\n  {el.name}")
        print(f"    position: {el.position.value}")

        if el.position == Position.FIXED:
            print(f"    bottom: {el.bottom}px" if el.bottom is not None else "")
            print(f"    left: {el.left}px" if el.left is not None else "")
            print(f"    z-index: {el.z_index}")

    print()
    print(f"  content margin-bottom: {layout.content_margin_bottom}px")
    print()

    # Simuler le scroll
    scroll_tests = [0, 300, 600, 1000]

    print("Simulation du scroll:")
    print("-" * 40)

    all_visible = True
    for scroll_y in scroll_tests:
        state = layout.simulate_scroll(scroll_y)
        print(f"\n  scroll_y = {scroll_y}px")
        print(f"    Visible: {', '.join(state.visible_elements)}")

        # Verifier que Input et Status sont visibles
        if not any("Input" in v for v in state.visible_elements):
            all_visible = False
        if not any("Status" in v for v in state.visible_elements):
            all_visible = False

    print()
    print("=" * 60)

    if all_visible:
        print("TOUS LES ELEMENTS RESTENT VISIBLES!")
        return True
    else:
        print("ERREUR: Certains elements disparaissent")
        return False


def show_css():
    """Affiche le CSS de la solution."""
    layout = FixedLayout()

    print("""
============================================================
CSS DE LA SOLUTION
============================================================
""")
    print(layout.get_css())


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Input et Status bar en position: static.
Ils disparaissent quand l'utilisateur scrolle vers le haut.

CORRECTION:
-----------
Appliquer position: fixed aux elements qui doivent rester visibles.

1. STATUS BAR:
   position: fixed;
   bottom: 0;           /* Colle en bas */
   left: 0; right: 0;   /* Pleine largeur */
   z-index: 1000;       /* Au-dessus de tout */

2. INPUT:
   position: fixed;
   bottom: 30px;        /* Au-dessus de status */
   left: 200px;         /* Apres sidebar */
   right: 0;
   z-index: 999;

3. CONTENU:
   margin-bottom: 100px; /* Espace pour fixed elements */

POURQUOI MARGIN-BOTTOM?
-----------------------
Les elements fixed sont retires du flux.
Sans margin, le contenu passe SOUS eux et devient invisible.

Z-INDEX:
--------
Status bar: 1000 (au-dessus de tout)
Input: 999 (juste en dessous de status)
Modals: 2000+ (au-dessus de tout si besoin)

============================================================
""")


def show_visualization():
    """Montre la visualisation apres correction."""
    print("""
============================================================
VISUALISATION APRES CORRECTION
============================================================

SCROLL = 0:
┌────────────────────────────────────────┐
│  Header (fixed)                        │
├────────────────────────────────────────┤
│  Message 8                             │
│  Message 9                             │
│  Message 10                            │
├────────────────────────────────────────┤
│  [Input________________________] (fixed)│
├────────────────────────────────────────┤
│  ● SYSTEM: ONLINE              (fixed) │
└────────────────────────────────────────┘

SCROLL = 1000 (vers le haut):
┌────────────────────────────────────────┐
│  Header (fixed)                        │
├────────────────────────────────────────┤
│  Message 1                             │
│  Message 2                             │
│  Message 3                             │
├────────────────────────────────────────┤
│  [Input________________________] (fixed)│  <- TOUJOURS LA!
├────────────────────────────────────────┤
│  ● SYSTEM: ONLINE              (fixed) │  <- TOUJOURS LA!
└────────────────────────────────────────┘

L'utilisateur peut toujours envoyer des messages!

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_css()
    print()
    show_explanation()
    show_visualization()
