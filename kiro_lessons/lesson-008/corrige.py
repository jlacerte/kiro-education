"""
Cours 008: Routes Admin Dashboard Manquantes
=============================================
CORRIGE - Solution Complete

Ce fichier montre les routes CORRIGEES.
Compare avec exercice.py pour voir la difference.
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
# APPLICATION CORRIGEE - TOUTES LES ROUTES DEFINIES
# ============================================================================

app = MockFastAPI()


# Route principale
@app.get("/admin")
async def admin_main():
    """Page principale du dashboard admin."""
    return {"template": "admin/base.html"}


# =============================================
# CORRECTION: Routes ajoutees!
# Chaque lien HTMX a maintenant sa route
# =============================================

@app.get("/admin/dashboard")
async def admin_dashboard():
    """Dashboard partiel pour HTMX."""
    return {"template": "admin/dashboard.html"}


@app.get("/admin/content")
async def admin_content():
    """Gestion de contenu partiel pour HTMX."""
    return {"template": "admin/content.html"}


@app.get("/admin/settings")
async def admin_settings():
    """Parametres partiel pour HTMX."""
    return {"template": "admin/settings.html"}


@app.get("/admin/audit")
async def admin_audit():
    """Journal d'audit partiel pour HTMX."""
    return {"template": "admin/audit.html"}


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


def run_tests():
    """Execute les tests corriges."""

    print("=" * 60)
    print("COURS 008 - CORRIGE - Toutes les Routes Definies")
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

    # Resultat
    ok_count = sum(1 for _, s in results if s == 200)
    total_count = len(results)

    print("=" * 60)
    print(f"RESULTAT: {ok_count}/{total_count} routes OK")
    print("=" * 60)

    if ok_count == total_count:
        print()
        print("TOUTES LES ROUTES SONT DEFINIES!")

    return ok_count == total_count


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Le template HTMX referencait des routes qui n'existaient pas.
Les requetes HTMX retournaient 404 Not Found.

CORRECTION:
-----------
Ajouter une route pour chaque lien hx-get:

    # AVANT (routes manquantes)
    @app.get("/admin")
    async def admin_main():
        ...
    # FIN - Pas d'autres routes!

    # APRES (routes ajoutees)
    @app.get("/admin")
    async def admin_main():
        ...

    @app.get("/admin/dashboard")
    async def admin_dashboard():
        ...

    @app.get("/admin/content")
    async def admin_content():
        ...

    @app.get("/admin/settings")
    async def admin_settings():
        ...

    @app.get("/admin/audit")
    async def admin_audit():
        ...

VERIFICATION:
-------------
Pour verifier que les routes existent:

    # Python
    for route in app.routes:
        print(route.path)

    # Ou via curl
    curl http://localhost:8000/admin/dashboard

ALTERNATIVE AVEC APIRouter:
---------------------------
Pour un code plus organise:

    # routes/admin.py
    from fastapi import APIRouter

    router = APIRouter(prefix="/admin", tags=["admin"])

    @router.get("/dashboard")
    async def dashboard():
        ...

    # main.py
    from routes.admin import router as admin_router
    app.include_router(admin_router)

============================================================
""")


def show_htmx_pattern():
    """Affiche le pattern HTMX avec detection."""
    print("""
============================================================
PATTERN AVANCE: DETECTION HTMX
============================================================

Pour servir une page complete ou un partial selon le contexte:

from fastapi import Request

@app.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    # Detecter si c'est une requete HTMX
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # Navigation HTMX -> partial seulement
        return templates.TemplateResponse(
            "admin/partials/dashboard.html",
            {"request": request}
        )
    else:
        # Acces direct -> page complete
        return templates.TemplateResponse(
            "admin/base.html",
            {"request": request, "section": "dashboard"}
        )

AVANTAGES:
- Meme URL pour les deux cas
- Fonctionne avec et sans JavaScript
- SEO friendly (la page complete est indexable)

============================================================
""")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
    print()
    show_explanation()
    show_htmx_pattern()
