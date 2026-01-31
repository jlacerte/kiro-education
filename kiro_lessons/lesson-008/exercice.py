"""
Cours 008: Routes Admin Dashboard Manquantes
=============================================
EXERCICE - Code a corriger

Niveau: Intermediaire
Duree: 25-35 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule une app FastAPI avec des routes manquantes
2. Lance le script pour voir quelles routes manquent
3. Ajoute les routes manquantes
4. Relance pour verifier

Pour lancer:
    python exercice.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


# ============================================================================
# SIMULATION D'UNE APPLICATION FASTAPI
# ============================================================================

@dataclass
class Route:
    """Represente une route HTTP."""
    path: str
    method: str = "GET"
    handler_name: str = ""

    def __hash__(self):
        return hash((self.path, self.method))


class MockFastAPI:
    """Simule une application FastAPI pour l'exercice."""

    def __init__(self):
        self.routes: List[Route] = []

    def get(self, path: str):
        """Decorateur pour ajouter une route GET."""
        def decorator(func):
            self.routes.append(Route(path=path, method="GET", handler_name=func.__name__))
            return func
        return decorator

    def post(self, path: str):
        """Decorateur pour ajouter une route POST."""
        def decorator(func):
            self.routes.append(Route(path=path, method="POST", handler_name=func.__name__))
            return func
        return decorator

    def get_route_paths(self) -> Set[str]:
        """Retourne l'ensemble des chemins de routes."""
        return {route.path for route in self.routes}


# ============================================================================
# APPLICATION AVEC ROUTES MANQUANTES - A CORRIGER
# ============================================================================

app = MockFastAPI()


# Route principale (existe)
@app.get("/admin")
async def admin_main():
    """Page principale du dashboard admin."""
    return {"template": "admin/base.html"}


# =============================================
# BUG: Routes manquantes!
# Le template base.html reference ces routes:
# - /admin/dashboard
# - /admin/content
# - /admin/settings
# - /admin/audit
# Mais elles n'existent pas!
# =============================================


# ============================================================================
# SIMULATION DU TEMPLATE HTMX
# ============================================================================

TEMPLATE_HTMX_LINKS = """
<!-- templates/admin/base.html -->
<nav class="admin-nav">
    <a href="/admin/dashboard" hx-get="/admin/dashboard" hx-target="#content">
        Dashboard
    </a>
    <a href="/admin/content" hx-get="/admin/content" hx-target="#content">
        Content
    </a>
    <a href="/admin/settings" hx-get="/admin/settings" hx-target="#content">
        Settings
    </a>
    <a href="/admin/audit" hx-get="/admin/audit" hx-target="#content">
        Audit Log
    </a>
</nav>
<main id="content">
    <!-- Contenu charge dynamiquement par HTMX -->
</main>
"""


def extract_htmx_routes(template: str) -> Set[str]:
    """Extrait les routes hx-get du template."""
    import re
    pattern = r'hx-get="([^"]+)"'
    matches = re.findall(pattern, template)
    return set(matches)


# ============================================================================
# ANALYSE ET VERIFICATION
# ============================================================================

def simulate_request(app: MockFastAPI, path: str) -> Dict:
    """Simule une requete HTTP."""
    routes = app.get_route_paths()

    if path in routes:
        return {"status_code": 200, "message": "OK"}
    else:
        return {"status_code": 404, "message": f"Not Found: {path}"}


def analyze_routes():
    """Analyse les routes definies vs les routes attendues."""

    print("=" * 60)
    print("COURS 008 - Routes Admin Dashboard Manquantes")
    print("=" * 60)
    print()

    # Routes definies dans l'application
    defined_routes = app.get_route_paths()

    # Routes attendues par le template
    expected_routes = extract_htmx_routes(TEMPLATE_HTMX_LINKS)

    print("Routes definies dans l'application:")
    print("-" * 40)
    for route in sorted(defined_routes):
        print(f"  [OK] {route}")
    print()

    print("Routes attendues par le template HTMX:")
    print("-" * 40)
    for route in sorted(expected_routes):
        status = "[OK]" if route in defined_routes else "[MANQUANTE]"
        print(f"  {status} {route}")
    print()

    # Simuler les requetes
    print("Simulation des requetes:")
    print("-" * 40)

    results = []
    all_routes = sorted(defined_routes | expected_routes)

    for path in all_routes:
        response = simulate_request(app, path)
        status = response["status_code"]
        icon = "200 OK" if status == 200 else "404 NOT FOUND"
        results.append((path, status))
        print(f"  GET {path:<25} -> {icon}")
    print()

    # Calculer les routes manquantes
    missing_routes = expected_routes - defined_routes
    ok_count = sum(1 for _, s in results if s == 200)
    total_count = len(results)

    print("=" * 60)
    print(f"RESULTAT: {ok_count}/{total_count} routes OK")
    print("=" * 60)
    print()

    if missing_routes:
        print("ROUTES MANQUANTES!")
        print("-" * 40)
        for route in sorted(missing_routes):
            print(f"  - {route}")
        print()
        print("SOLUTION:")
        print("-" * 40)
        print("""
Pour chaque route manquante, ajouter:

    @app.get("/admin/dashboard")
    async def admin_dashboard():
        return {"template": "admin/dashboard.html"}

    @app.get("/admin/content")
    async def admin_content():
        return {"template": "admin/content.html"}

    @app.get("/admin/settings")
    async def admin_settings():
        return {"template": "admin/settings.html"}

    @app.get("/admin/audit")
    async def admin_audit():
        return {"template": "admin/audit.html"}

Ou utiliser un APIRouter:

    from fastapi import APIRouter

    admin_router = APIRouter(prefix="/admin")

    @admin_router.get("/dashboard")
    async def dashboard():
        ...
""")
        return False
    else:
        print("TOUTES LES ROUTES SONT DEFINIES!")
        return True


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_routes()
