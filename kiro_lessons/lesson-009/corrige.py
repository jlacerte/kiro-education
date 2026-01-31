"""
Cours 009: Fixation Fonctionnelle - Script Charge au Mauvais Endroit
====================================================================
CORRIGE - Solution Complete

Ce fichier montre la solution CORRIGEE.
Compare avec exercice.py pour voir la difference.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable


# ============================================================================
# SIMULATION D'UN SYSTEME DE TEMPLATES
# ============================================================================

@dataclass
class Script:
    """Represente un script JavaScript."""
    name: str
    path: str
    content: str
    condition: Optional[Callable[[str], bool]] = None  # NOUVEAU: condition de chargement


@dataclass
class Page:
    """Represente une page HTML rendue."""
    url: str
    title: str
    content: str
    scripts_loaded: List[str] = field(default_factory=list)


class TemplateEngine:
    """Simule un moteur de templates avec chargement conditionnel."""

    def __init__(self):
        self.scripts: List[Script] = []
        self.pages: Dict[str, dict] = {}

    def add_script(self, script: Script):
        """Ajoute un script (avec condition optionnelle)."""
        self.scripts.append(script)

    def register_page(self, url: str, title: str, content: str):
        """Enregistre une page."""
        self.pages[url] = {"title": title, "content": content}

    def render(self, url: str) -> Page:
        """Rend une page avec les scripts CONDITIONNELS."""
        if url not in self.pages:
            return Page(url=url, title="404", content="Not Found", scripts_loaded=[])

        page_data = self.pages[url]

        # =============================================
        # CORRECTION: Charger les scripts selon leur condition
        # =============================================
        scripts_loaded = []
        for script in self.scripts:
            if script.condition is None:
                # Pas de condition = charger partout
                scripts_loaded.append(script.name)
            elif script.condition(url):
                # Condition satisfaite = charger
                scripts_loaded.append(script.name)
            # Sinon, ne pas charger!

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
            if script.name == "artifacts.js":
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

    return final_content


# ============================================================================
# APPLICATION CORRIGEE
# ============================================================================

# Creer le moteur de templates
engine = TemplateEngine()

# Definir les scripts avec CONDITIONS
main_script = Script(
    name="main.js",
    path="/static/js/main.js",
    content="// Fonctions utilitaires",
    condition=None  # Charger partout
)

# =============================================
# CORRECTION: artifacts.js a une condition!
# Ne se charge que si l'URL ne commence pas par /admin
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
""",
    condition=lambda url: not url.startswith("/admin")  # CORRECTION!
)

admin_script = Script(
    name="admin.js",
    path="/static/js/admin.js",
    content="console.log('Dashboard initialized');",
    condition=lambda url: url.startswith("/admin")  # Seulement sur /admin
)

# Ajouter les scripts (avec leurs conditions)
engine.add_script(main_script)
engine.add_script(artifacts_script)
engine.add_script(admin_script)

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
# VERIFICATION
# ============================================================================

def run_tests():
    """Execute les tests corriges."""

    print("=" * 60)
    print("COURS 009 - CORRIGE - Chargement Conditionnel")
    print("=" * 60)
    print()

    all_scripts = [main_script, artifacts_script, admin_script]

    # Tester chaque page
    pages_to_test = ["/", "/artifacts", "/admin"]
    results = []

    for url in pages_to_test:
        page = engine.render(url)
        final_content = simulate_script_execution(page, all_scripts)

        is_correct = True
        if url == "/admin":
            if "Artefacts" in final_content:
                is_correct = False
            elif "metrics" not in final_content:
                is_correct = False

        results.append({
            "url": url,
            "scripts": page.scripts_loaded,
            "is_correct": is_correct,
        })

    # Afficher les resultats
    print("Scripts charges par page:")
    print("-" * 40)

    for result in results:
        status = "OK" if result["is_correct"] else "BUG"
        print(f"\n  {result['url']}")
        print(f"    Scripts: {', '.join(result['scripts']) or 'aucun'}")
        print(f"    Status: [{status}]")

    print()
    print("=" * 60)

    if all(r["is_correct"] for r in results):
        print("TOUTES LES PAGES FONCTIONNENT!")
        return True
    else:
        print("ERREURS DETECTEES")
        return False


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
artifacts.js etait charge sur TOUTES les pages.
Sur /admin, il ecrasait le contenu du dashboard.

CORRECTION (2 lignes!):
-----------------------
Dans base.html:

    {% if not request.url.path.startswith('/admin') %}
    <script src="/static/js/artifacts.js"></script>
    {% endif %}

POURQUOI CA MARCHE:
-------------------
Pas de script = pas de probleme.

Au lieu de GERER le fait que le script s'execute au mauvais endroit,
on ELIMINE le probleme a la source en ne chargeant pas le script.

============================================================
""")


def show_lesson():
    """Affiche la lecon de cette correction."""
    print("""
============================================================
LECON: ELIMINER PLUTOT QUE GERER
============================================================

AVANT de corriger un bug, posez-vous cette question:

    "Est-ce que ce code devrait exister ici en premier lieu?"

Si la reponse est NON, la solution est souvent d'ELIMINER
le code plutot que de GERER ses effets secondaires.

COMPARAISON:
------------
Approche "GERER":
  - Ajouter des conditions dans le script
  - Verifier le pathname
  - Intercepter les requetes HTMX
  - 2+ heures de debug, code fragile

Approche "ELIMINER":
  - Ne pas charger le script
  - 30 secondes, solution robuste

LA FIXATION FONCTIONNELLE:
--------------------------
C'est rester bloque sur la question:
  "Comment empecher ce script de s'executer?"

Au lieu de se demander:
  "Pourquoi ce script est-il charge ici?"

============================================================
""")


def show_pattern():
    """Affiche le pattern de chargement conditionnel."""
    print("""
============================================================
PATTERN: CHARGEMENT CONDITIONNEL DE SCRIPTS
============================================================

OPTION 1: Condition Jinja simple
--------------------------------
{% if not request.url.path.startswith('/admin') %}
<script src="/static/js/artifacts.js"></script>
{% endif %}


OPTION 2: Scripts par section (block)
-------------------------------------
<!-- base.html -->
<script src="/static/js/main.js"></script>
{% block scripts %}{% endblock %}

<!-- admin/base.html -->
{% block scripts %}
<script src="/static/js/admin.js"></script>
{% endblock %}

<!-- artifacts.html -->
{% block scripts %}
<script src="/static/js/artifacts.js"></script>
{% endblock %}


OPTION 3: Chargement dynamique
------------------------------
<body data-page="{{ page_name }}">
<script>
const modules = {
    'admin': '/static/js/admin.js',
    'artifacts': '/static/js/artifacts.js'
};
const page = document.body.dataset.page;
if (modules[page]) {
    import(modules[page]);
}
</script>

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_explanation()
    show_lesson()
    show_pattern()
