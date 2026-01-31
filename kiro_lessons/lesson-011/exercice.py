"""
Cours 011: CSS Layout - Consolidation des Status Bars
=====================================================
EXERCICE - Code a corriger

Niveau: Intermediaire
Duree: 25-35 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un layout avec 3 status bars redondantes
2. Lance le script pour voir le probleme
3. Consolide les informations en une seule status line
4. Elimine les elements inutiles

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass
from typing import List, Dict


# ============================================================================
# MODELES DE DONNEES
# ============================================================================

@dataclass
class StatusBar:
    """Represente une barre de status."""
    name: str
    height_px: int
    items: List[str]
    is_useful: bool = True


@dataclass
class LayoutAnalysis:
    """Analyse d'un layout."""
    total_height: int
    useful_height: int
    wasted_height: int
    redundant_items: List[str]


# ============================================================================
# LAYOUT AVEC STATUS BARS REDONDANTES - A CORRIGER
# ============================================================================

class TerminalLayout:
    """Simule un layout de terminal avec status bars."""

    def __init__(self):
        # =============================================
        # BUG: Trop de status bars!
        # =============================================
        self.status_bars: List[StatusBar] = [
            StatusBar(
                name="Connection Status",
                height_px=30,
                items=["Connected", "1 artifact", "4 videos", "01:32"],
                is_useful=True
            ),
            StatusBar(
                name="Function Keys",
                height_px=28,
                items=["F1 Help", "F2 Menu", "F3 View", "F4 Edit", "F5 Copy",
                       "F6 Move", "F7 Mkdir", "F8 Delete", "F9 Menu", "F10 Quit"],
                is_useful=False  # Jamais utilisee!
            ),
            StatusBar(
                name="System Footer",
                height_px=32,
                items=["SYSTEM: ONLINE", "MEMORY: N/A", "UPTIME: N/A"],
                is_useful=True
            ),
        ]

        # Element flottant supplementaire
        self.floating_elements = [
            {"name": "Sound Indicator", "height": 20, "content": "SOUND: OFF"}
        ]

        self.header_height = 50
        self.content_area_base = 400

    def get_total_status_height(self) -> int:
        """Calcule la hauteur totale des status bars."""
        bar_height = sum(bar.height_px for bar in self.status_bars)
        float_height = sum(el["height"] for el in self.floating_elements)
        return bar_height + float_height

    def get_available_content_height(self, viewport_height: int) -> int:
        """Calcule l'espace disponible pour le contenu."""
        used = self.header_height + self.get_total_status_height()
        return viewport_height - used

    def find_redundant_info(self) -> List[str]:
        """Trouve les informations redondantes entre les barres."""
        all_items = []
        for bar in self.status_bars:
            all_items.extend(bar.items)

        # Chercher les doublons conceptuels
        redundant = []

        # Connexion mentionnee plusieurs fois?
        connection_items = [i for i in all_items if "connect" in i.lower() or "online" in i.lower()]
        if len(connection_items) > 1:
            redundant.append(f"Connexion: {connection_items}")

        # Temps mentionne plusieurs fois?
        time_items = [i for i in all_items if ":" in i and any(c.isdigit() for c in i)]
        if len(time_items) > 1:
            redundant.append(f"Temps: {time_items}")

        return redundant

    def analyze(self) -> LayoutAnalysis:
        """Analyse le layout actuel."""
        total_height = self.get_total_status_height()
        useful_height = sum(bar.height_px for bar in self.status_bars if bar.is_useful)
        wasted_height = total_height - useful_height

        return LayoutAnalysis(
            total_height=total_height,
            useful_height=useful_height,
            wasted_height=wasted_height,
            redundant_items=self.find_redundant_info()
        )


# ============================================================================
# ANALYSE ET VERIFICATION
# ============================================================================

def analyze_layout():
    """Analyse le layout et montre les problemes."""

    print("=" * 60)
    print("COURS 011 - Consolidation des Status Bars")
    print("=" * 60)
    print()

    layout = TerminalLayout()

    # Afficher les status bars actuelles
    print("Status Bars actuelles:")
    print("-" * 40)

    for bar in layout.status_bars:
        useful = "[UTILE]" if bar.is_useful else "[INUTILE]"
        print(f"\n  {bar.name} {useful}")
        print(f"  Hauteur: {bar.height_px}px")
        print(f"  Items: {', '.join(bar.items[:4])}{'...' if len(bar.items) > 4 else ''}")

    print()

    for el in layout.floating_elements:
        print(f"\n  {el['name']} [FLOTTANT]")
        print(f"  Hauteur: {el['height']}px")
        print(f"  Contenu: {el['content']}")

    print()

    # Analyse
    analysis = layout.analyze()

    print("Analyse du layout:")
    print("-" * 40)
    print(f"  Hauteur totale status bars: {analysis.total_height}px")
    print(f"  Hauteur utile: {analysis.useful_height}px")
    print(f"  Hauteur gaspillee: {analysis.wasted_height}px")

    # Viewport simulation
    viewport = 800
    available = layout.get_available_content_height(viewport)

    print()
    print(f"  Viewport: {viewport}px")
    print(f"  Header: {layout.header_height}px")
    print(f"  Status bars: {analysis.total_height}px")
    print(f"  Disponible pour contenu: {available}px ({available*100//viewport}%)")

    print()

    # Verdict
    print("=" * 60)

    if analysis.wasted_height > 0 or len(layout.status_bars) > 1:
        print("PROBLEMES DETECTES!")
        print("-" * 40)
        print()
        print(f"  - {len(layout.status_bars)} status bars (devrait etre 1)")
        print(f"  - {analysis.wasted_height}px gaspilles")
        print(f"  - Seulement {available*100//viewport}% de l'ecran pour le contenu")
        print()
        print("SOLUTION:")
        print("-" * 40)
        print("""
  1. Supprimer la barre F-keys (jamais utilisee):
     .function-keys-bar { display: none; }

  2. Consolider en UNE SEULE status line:
     ● SYSTEM: ONLINE | MEM: 38% | UPTIME: 2h | 14:32 | SOUND: OFF

  3. Deplacer les stats contenu dans la sidebar:
     Sidebar: 4 Videos | 1 Channel | 1 Artifact

  4. Cacher les elements flottants redondants:
     .sound-indicator-float { display: none; }
""")
        return False
    else:
        print("LAYOUT OPTIMISE!")
        return True


def show_comparison():
    """Montre la comparaison avant/apres."""
    print("""
============================================================
COMPARAISON AVANT/APRES
============================================================

AVANT (3 barres + flottant):
┌──────────────────────────────────────────────────────┐
│                    CONTENU                           │
│                  (petite zone)                       │
├──────────────────────────────────────────────────────┤
│ ● Connected | 1 artifact | 4 videos | 01:32         │  30px
├──────────────────────────────────────────────────────┤
│ F1 Help | F2 Menu | F3 View | ... | F10 Quit        │  28px
├──────────────────────────────────────────────────────┤
│ SYSTEM: ONLINE | MEMORY: N/A | UPTIME: N/A          │  32px
└──────────────────────────────────────────────────────┘
  SOUND: OFF (flottant)                                   20px
                                            TOTAL: 110px

APRES (1 seule barre):
┌──────────────────────────────────────────────────────┐
│                                                      │
│                    CONTENU                           │
│                (grande zone!)                        │
│                                                      │
├──────────────────────────────────────────────────────┤
│ ● SYSTEM: ONLINE | MEM: 38% | UPTIME: 2h | SOUND    │  28px
└──────────────────────────────────────────────────────┘
                                            TOTAL: 28px

GAIN: 82px d'espace vertical!
============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_layout()
    print()
    show_comparison()
