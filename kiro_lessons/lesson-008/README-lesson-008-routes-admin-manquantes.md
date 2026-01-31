# Cours 008: Routes Admin Dashboard Manquantes

## Niveau: Intermediaire

## Duree estimee: 25-35 minutes

## Prerequis

- Bases de Python
- Notions de FastAPI
- Comprendre les templates HTML
- Notions de HTMX (optionnel)

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur un dashboard admin qui utilise HTMX pour la navigation. Les boutons de navigation ne fonctionnent pas - ils affichent une erreur 404.

### Code problematique

**Fichier**: `templates/admin/base.html`

```html
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
</nav>
<div id="content">
    <!-- Contenu charge ici -->
</div>
```

**Fichier**: `main.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/admin")
async def admin():
    return templates.TemplateResponse("admin/base.html", {"request": request})

# Les routes /admin/dashboard, /admin/content, /admin/settings N'EXISTENT PAS!
```

### Le probleme

```bash
GET /admin           -> 200 OK
GET /admin/dashboard -> 404 Not Found
GET /admin/content   -> 404 Not Found
GET /admin/settings  -> 404 Not Found
```

Les templates referencent des routes qui n'existent pas dans le backend!

---

## Partie 2: Ta Mission

### Objectif

Ajouter les routes manquantes pour que la navigation HTMX fonctionne.

### Options de correction

| Option | Methode | Quand l'utiliser |
|--------|---------|------------------|
| A | Routes individuelles | Petit projet, peu de routes |
| B | APIRouter dedie | Projet structure, beaucoup de routes |
| C | Modifier templates | Si on ne veut pas de HTMX |

### Questions a se poser

1. Combien de routes admin aura-t-on a terme?
2. Veut-on garder HTMX pour la navigation?
3. Les templates partials sont-ils prets?

### Indices

<details>
<summary>Indice 1: Structure d'une route FastAPI</summary>

```python
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request}
    )
```

</details>

<details>
<summary>Indice 2: Utiliser un Router</summary>

```python
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
async def dashboard():
    ...

# Dans main.py
app.include_router(router)
```

</details>

<details>
<summary>Indice 3: Retourner du HTML partiel</summary>

Pour HTMX, on retourne souvent un fragment HTML (partial), pas une page complete:

```python
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_partial(request: Request):
    # Retourne SEULEMENT le contenu, pas le layout complet
    return templates.TemplateResponse(
        "admin/partials/dashboard.html",
        {"request": request}
    )
```

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Comprendre le probleme

```bash
python exercice.py
```

L'analyseur va montrer les routes manquantes.

### Etape 2: Choisir une solution

- Petit projet? -> Option A (routes individuelles)
- Projet structure? -> Option B (APIRouter)
- Pas de HTMX? -> Option C (modifier templates)

### Etape 3: Implementer

Modifie `exercice.py` pour ajouter les routes manquantes.

---

## Partie 4: Corrige (Solutions Completes)

### Option A: Routes individuelles (Simple)

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/admin", response_class=HTMLResponse)
async def admin_main(request: Request):
    return templates.TemplateResponse("admin/base.html", {"request": request})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@app.get("/admin/content", response_class=HTMLResponse)
async def admin_content(request: Request):
    return templates.TemplateResponse("admin/content.html", {"request": request})

@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    return templates.TemplateResponse("admin/settings.html", {"request": request})
```

**Avantages**: Simple, direct
**Inconvenients**: Code duplique si beaucoup de routes

### Option B: APIRouter (Recommande pour projets structures)

**Fichier**: `routes/admin.py`

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("", response_class=HTMLResponse)
async def admin_main(request: Request):
    from main import templates
    return templates.TemplateResponse("admin/base.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    from main import templates
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@router.get("/content", response_class=HTMLResponse)
async def admin_content(request: Request):
    from main import templates
    return templates.TemplateResponse("admin/content.html", {"request": request})

@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    from main import templates
    return templates.TemplateResponse("admin/settings.html", {"request": request})
```

**Fichier**: `main.py`

```python
from routes.admin import router as admin_router
app.include_router(admin_router)
```

**Avantages**: Code organise, prefix automatique, tags pour docs
**Inconvenients**: Un fichier de plus

---

## Partie 5: Lecons Apprises

### 1. Coherence templates/routes

```python
# MAUVAIS - Le template reference une route qui n'existe pas
# Template: hx-get="/admin/dashboard"
# Routes: seulement /admin existe

# BON - Chaque hx-get a une route correspondante
@app.get("/admin/dashboard")  # <- Route existe
async def dashboard(): ...
```

### 2. Verifier les routes existantes

```python
# Lister toutes les routes de l'application
for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### 3. Pattern HTMX: partials vs pages completes

```python
# Page complete (premiere visite)
@app.get("/admin")
async def admin_page():
    return templates.TemplateResponse("admin/base.html", ...)

# Partial (navigation HTMX)
@app.get("/admin/dashboard")
async def admin_dashboard_partial():
    return templates.TemplateResponse("admin/partials/dashboard.html", ...)
```

### 4. Organisation avec APIRouter

```
src/
├── main.py              # app = FastAPI()
└── routes/
    ├── admin.py         # router = APIRouter(prefix="/admin")
    ├── api.py           # router = APIRouter(prefix="/api")
    └── auth.py          # router = APIRouter(prefix="/auth")
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi les boutons de navigation affichent 404?

<details>
<summary>Reponse</summary>
Les templates HTMX referencent des routes (`/admin/dashboard`, etc.) qui n'ont pas ete definies dans le backend FastAPI. Le serveur ne sait pas comment repondre a ces URLs.
</details>

### Question 2
Quelle est la difference entre `@app.get()` et `@router.get()`?

<details>
<summary>Reponse</summary>
- `@app.get()`: Definit une route directement sur l'application principale
- `@router.get()`: Definit une route sur un router qui sera inclus dans l'app via `app.include_router()`

Le router permet d'organiser les routes par domaine et d'ajouter un prefix automatiquement.
</details>

### Question 3
Comment lister toutes les routes d'une application FastAPI?

<details>
<summary>Reponse</summary>

```python
for route in app.routes:
    if hasattr(route, 'methods'):
        print(f"{route.methods} {route.path}")
```

Ou utiliser la documentation auto-generee: `http://localhost:8000/docs`
</details>

---

## Partie 7: Patterns de Routing

### Pattern: Routes hierarchiques

```python
# Routes imbriquees avec prefixes
main_router = APIRouter()
admin_router = APIRouter(prefix="/admin")
api_router = APIRouter(prefix="/api")

admin_router.include_router(settings_router, prefix="/settings")
# -> /admin/settings/...

main_router.include_router(admin_router)
main_router.include_router(api_router)

app.include_router(main_router)
```

### Pattern: Routes HTMX avec detection

```python
@app.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    # Detecter si c'est une requete HTMX
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # Retourner seulement le partial
        return templates.TemplateResponse("admin/partials/dashboard.html", ...)
    else:
        # Retourner la page complete
        return templates.TemplateResponse("admin/base.html", ...)
```

---

## Ressources Supplementaires

- [FastAPI Routing](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/reference/apirouter/)
- [HTMX Documentation](https://htmx.org/docs/)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
