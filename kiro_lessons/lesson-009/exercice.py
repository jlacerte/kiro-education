"""
Cours 009: Fixation Fonctionnelle - Script Charge au Mauvais Endroit
====================================================================
EXERCICE - Code a corriger

Niveau: Intermediaire
Duree: 30-40 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule un bug ou un script s'execute au mauvais endroit
2. Lance le script pour voir le probleme
3. Trouve la VRAIE cause du probleme
4. Corrige-le de la maniere la plus simple possible

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================================
# SIMULATION D'UN SYSTEME DE TEMPLATES
# ============================================================================

@dataclass
class Script:
    """Represente un script JavaScript."""
    name: str
    path: str
    content: str
    loaded_on: List[str] = field(default_factory=list)


@dataclass
class Page:
    """Represente une page HTML rendue."""
    url: str
    title: str
    content: str
    scripts_loaded: List[str] = field(default_factory=list)


class TemplateEngine:
    """Simule un moteur de templates avec scripts globaux."""

    def __init__(self):
        self.global_scripts: List[Script] = []
        self.pages: Dict[str, dict] = {}

    def add_global_script(self, script: Script):
        """Ajoute un script charge sur TOUTES les pages."""
        self.global_scripts.append(script)

    def register_page(self, url: str, title: str, content: str):
        """Enregistre une page."""
        self.pages[url] = {"title": title, "content": content}

    def render(self, url: str) -> Page:
        """Rend une page avec tous ses scripts."""
        if url not in self.pages:
            return Page(url=url, title="404", content="Not Found", scripts_loaded=[])

        page_data = self.pages[url]

        # Tous les scripts globaux sont charges
        scripts_loaded = [s.name for s in self.global_scripts]

        return Page(
            url=url,
            title=page_data["title"],
            content=page_data["content"],
            scripts_loaded=scripts_loaded
        )


# ============================================================================
# SIMULATION DES SCRIPTS
# ============================================================================

def simulate_script_execution(page: Page, scripts: List[Script]) -> str:
    """Simule l'execution des scripts sur une page."""

    final_content = page.content

    for script in scripts:
        if script.name in page.scripts_loaded:
            # Simuler l'effet du script
            if script.name == "artifacts.js":
                # Ce script ECRASE le contenu avec la liste d'artefacts!
                final_content = """
<div id="artifacts-list">
  <h2>Artefacts</h2>
  <ul>
    <li>Summary: How to Build RAG Systems</li>
    <li>FAQ: Machine Learning Basics</li>
    <li>Podcast: AI News Weekly</li>
  </ul>
</div>
"""
            elif script.name == "admin.js":
                # Ce script initialise le dashboard (ne change pas le contenu)
                pass

    return final_content


# ============================================================================
# APPLICATION AVEC BUG - A CORRIGER
# ============================================================================

# Creer le moteur de templates
engine = TemplateEngine()

# Definir les scripts
main_script = Script(
    name="main.js",
    path="/static/js/main.js",
    content="// Fonctions utilitaires"
)

# =============================================
# BUG: artifacts.js est charge GLOBALEMENT!
# Il s'execute sur TOUTES les pages, meme /admin
# =============================================
artifacts_script = Script(
    name="artifacts.js",
    path="/static/js/artifacts.js",
    content="""
document.addEventListener('DOMContentLoaded', function() {
    htmx.ajax('GET', '/api/artifacts/list', {
        target: '#content',
        swap: 'innerHTML'
    });
});
"""
)

admin_script = Script(
    name="admin.js",
    path="/static/js/admin.js",
    content="console.log('Dashboard initialized');"
)

# Ajouter les scripts GLOBAUX (le probleme est ici!)
engine.add_global_script(main_script)
engine.add_global_script(artifacts_script)  # BUG: Ne devrait pas etre global!
engine.add_global_script(admin_script)

# Definir les pages
engine.register_page(
    "/",
    "Home - Blade Runner",
    "<h1>Welcome</h1><div id='content'>Home content</div>"
)

engine.register_page(
    "/artifacts",
    "Artifacts - Blade Runner",
    "<h1>Artifacts</h1><div id='content'>Loading...</div>"
)

engine.register_page(
    "/admin",
    "Admin Dashboard - Blade Runner",
    """<h1>Admin Dashboard</h1>
<div id='content'>
  <div class='metrics'>
    <div>Videos: 42</div>
    <div>Transcripts: 38</div>
    <div>Storage: 1.2 GB</div>
    <div>API Calls: 1,234</div>
  </div>
</div>"""
)


# ============================================================================
# ANALYSE ET VERIFICATION
# ============================================================================

def analyze_bug():
    """Analyse le bug et montre le probleme."""

    print("=" * 60)
    print("COURS 009 - Fixation Fonctionnelle")
    print("=" * 60)
    print()

    all_scripts = [main_script, artifacts_script, admin_script]

    # Afficher la configuration des scripts
    print("Scripts charges GLOBALEMENT:")
    print("-" * 40)
    for script in engine.global_scripts:
        print(f"  - {script.name}")
    print()

    # Tester chaque page
    pages_to_test = ["/", "/artifacts", "/admin"]
    results = []

    for url in pages_to_test:
        page = engine.render(url)
        final_content = simulate_script_execution(page, all_scripts)

        # Verifier si le contenu est correct
        is_correct = True
        problem = None

        if url == "/admin":
            if "Artefacts" in final_content:
                is_correct = False
                problem = "Affiche les artefacts au lieu des metriques!"
            elif "metrics" not in final_content:
                is_correct = False
                problem = "Metriques manquantes"

        results.append({
            "url": url,
            "title": page.title,
            "scripts": page.scripts_loaded,
            "is_correct": is_correct,
            "problem": problem,
            "final_content": final_content[:100] + "..." if len(final_content) > 100 else final_content
        })

    # Afficher les resultats
    print("Test des pages:")
    print("-" * 40)

    for result in results:
        status = "OK" if result["is_correct"] else "BUG"
        print(f"\n  URL: {result['url']}")
        print(f"  Titre: {result['title']}")
        print(f"  Scripts: {', '.join(result['scripts'])}")
        print(f"  Status: [{status}]")
        if result["problem"]:
            print(f"  Probleme: {result['problem']}")

    print()
    print("=" * 60)

    # Resultat global
    bugs = [r for r in results if not r["is_correct"]]

    if bugs:
        print("BUG DETECTE!")
        print("-" * 40)
        print()
        print("PROBLEME:")
        print("  Le script 'artifacts.js' est charge sur TOUTES les pages,")
        print("  y compris /admin ou il ecrase le contenu du dashboard.")
        print()
        print("MAUVAISES SOLUTIONS (ne pas utiliser):")
        print("-" * 40)
        print("""
  1. IIFE avec early return dans artifacts.js
     -> Le script est quand meme parse

  2. Verification du pathname dans le script
     -> Race condition avec HTMX

  3. CSS pour cacher le contenu
     -> Ne resout pas l'ecrasement du DOM

  4. Bloquer l'API /api/artifacts/list sur /admin
     -> Casse d'autres fonctionnalites
""")
        print("BONNE QUESTION A SE POSER:")
        print("-" * 40)
        print('  "Pourquoi ce script est-il charge ici en premier lieu?"')
        print()
        print("SOLUTION:")
        print("-" * 40)
        print("""
  Ne pas charger artifacts.js sur les pages admin!

  Dans base.html:
    {% if not request.url.path.startswith('/admin') %}
    <script src="/static/js/artifacts.js"></script>
    {% endif %}
""")
        return False
    else:
        print("TOUTES LES PAGES FONCTIONNENT CORRECTEMENT!")
        return True


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_bug()
