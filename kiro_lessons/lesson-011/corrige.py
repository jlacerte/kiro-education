"""
Cours 011: CSS Layout - Consolidation des Status Bars
=====================================================
CORRIGE - Solution Complete

Ce fichier montre le layout CORRIGE avec une seule status line.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass
from typing import List, Dict


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class StatusItem:
    """Un element de la status line."""
    label: str
    value: str
    is_clickable: bool = False


@dataclass
class StatusLine:
    """La status line unique et consolidee."""
    height_px: int
    items: List[StatusItem]


@dataclass
class SidebarStats:
    """Stats de contenu dans la sidebar."""
    videos: int
    artifacts: int
    channels: int


# ============================================================================
# LAYOUT CORRIGE - UNE SEULE STATUS LINE
# ============================================================================

class OptimizedLayout:
    """Layout optimise avec status line unique."""

    def __init__(self):
        # =============================================
        # CORRECTION: Une seule status line!
        # =============================================
        self.status_line = StatusLine(
            height_px=28,
            items=[
                StatusItem("SYSTEM", "ONLINE", is_clickable=False),
                StatusItem("MEM", "38%", is_clickable=False),
                StatusItem("UPTIME", "2h", is_clickable=False),
                StatusItem("TIME", "14:32", is_clickable=False),
                StatusItem("SOUND", "OFF", is_clickable=True),
            ]
        )

        # Stats contenu -> dans la sidebar
        self.sidebar_stats = SidebarStats(
            videos=4,
            artifacts=1,
            channels=1
        )

        self.header_height = 50

    def get_total_status_height(self) -> int:
        """Hauteur totale des elements de status."""
        return self.status_line.height_px

    def get_available_content_height(self, viewport_height: int) -> int:
        """Calcule l'espace disponible pour le contenu."""
        used = self.header_height + self.get_total_status_height()
        return viewport_height - used

    def render_status_line(self) -> str:
        """Genere le rendu de la status line."""
        parts = []

        # Dot de connexion
        parts.append("●")

        for item in self.status_line.items:
            parts.append(f"{item.label}: {item.value}")

        return " | ".join(parts)

    def render_sidebar_stats(self) -> str:
        """Genere le rendu des stats sidebar."""
        return f"""
  ─────────────
  CONTENT STATS
  ─────────────
  📺 {self.sidebar_stats.videos} Videos
  📄 {self.sidebar_stats.artifacts} Artifacts
  📡 {self.sidebar_stats.channels} Channels
"""


# ============================================================================
# VERIFICATION
# ============================================================================

def run_tests():
    """Execute les tests du layout optimise."""

    print("=" * 60)
    print("COURS 011 - CORRIGE - Status Line Unique")
    print("=" * 60)
    print()

    layout = OptimizedLayout()

    # Afficher la status line
    print("Status Line (SYSTEME):")
    print("-" * 40)
    print(f"  Hauteur: {layout.status_line.height_px}px")
    print(f"  Rendu: {layout.render_status_line()}")
    print()

    # Afficher les stats sidebar
    print("Sidebar Stats (CONTENU):")
    print("-" * 40)
    print(layout.render_sidebar_stats())

    # Analyse de l'espace
    viewport = 800
    available = layout.get_available_content_height(viewport)
    status_height = layout.get_total_status_height()

    print("Analyse de l'espace:")
    print("-" * 40)
    print(f"  Viewport: {viewport}px")
    print(f"  Header: {layout.header_height}px")
    print(f"  Status line: {status_height}px")
    print(f"  Disponible: {available}px ({available*100//viewport}%)")
    print()

    # Comparaison avec l'ancien layout
    old_status_height = 110  # 30 + 28 + 32 + 20
    old_available = viewport - layout.header_height - old_status_height
    gain = available - old_available

    print("Comparaison:")
    print("-" * 40)
    print(f"  Ancien: {old_available}px disponibles ({old_available*100//viewport}%)")
    print(f"  Nouveau: {available}px disponibles ({available*100//viewport}%)")
    print(f"  Gain: +{gain}px (+{gain*100//viewport}%)")
    print()

    print("=" * 60)
    print("LAYOUT OPTIMISE!")
    print(f"  Status line unique: {status_height}px")
    print(f"  Gain d'espace: +{gain}px")

    return True


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
3 status bars + 1 element flottant = 110px perdus.
Redondance d'information et confusion visuelle.

CORRECTION:
-----------
1. UNE SEULE status line systeme (28px):
   ● SYSTEM: ONLINE | MEM: 38% | UPTIME: 2h | 14:32 | SOUND: OFF

2. Stats contenu -> Sidebar:
   📺 4 Videos | 📄 1 Artifacts | 📡 1 Channels

3. Supprimer les elements inutiles:
   - F-keys bar (jamais utilisee)
   - Sound indicator flottant (integre dans status line)
   - Footer redondant

CSS UTILISE:
------------
/* Cacher les elements inutiles */
.function-keys-bar { display: none !important; }
.sound-indicator-float { display: none !important; }
.dual-pane-layout:has(.mc-status-bar) .footer { display: none; }

/* Status line unique */
.mc-status-bar {
    height: 28px;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to bottom, #1a1a2e, #0f0f1a);
    border-top: 1px solid #00ff41;
    display: flex;
    align-items: center;
    padding: 0 15px;
    gap: 8px;
}

============================================================
""")


def show_separation():
    """Montre la separation des responsabilites."""
    print("""
============================================================
SEPARATION DES RESPONSABILITES
============================================================

SIDEBAR (Stats Contenu):          STATUS LINE (Stats Systeme):
─────────────────────────         ──────────────────────────
Ce que l'utilisateur A:           Comment va l'application:

📺 4 Videos                       ● SYSTEM: ONLINE
📄 1 Artifacts                    MEM: 38%
📡 1 Channels                     UPTIME: 2h
                                  TIME: 14:32
                                  SOUND: OFF

POURQUOI CETTE SEPARATION?
--------------------------
- Sidebar: l'utilisateur peut agir dessus (cliquer pour voir)
- Status line: info passive, "pouls" de l'application
- Pas de confusion: chaque zone a un role clair

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_explanation()
    show_separation()
