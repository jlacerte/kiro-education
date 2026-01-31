# Cours 009: Fixation Fonctionnelle - Script Charge au Mauvais Endroit

## Niveau: Intermediaire

## Duree estimee: 30-40 minutes

## Prerequis

- Bases de HTML/JavaScript
- Notions de templates (Jinja2)
- Comprendre le chargement de scripts

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur un dashboard admin. La page `/admin` devrait afficher des metriques systeme, mais elle affiche mysterieusement une liste d'artefacts a la place.

### Symptomes observes

```
URL: /admin
Titre: "Admin Dashboard" (correct)
Console: "Dashboard initialized" (correct)
Contenu: Liste d'artefacts (INCORRECT!)
Attendu: Metriques systeme (CPU, RAM, etc.)
```

### Code problematique

**Fichier**: `templates/base.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}App{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}

    <!-- Scripts charges globalement -->
    <script src="/static/js/main.js"></script>
    <script src="/static/js/artifacts.js"></script>  <!-- PROBLEME! -->
</body>
</html>
```

**Fichier**: `static/js/artifacts.js`

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Ce code s'execute sur TOUTES les pages!
    htmx.ajax('GET', '/api/artifacts/list', {
        target: '#content',
        swap: 'innerHTML'
    });
});
```

### Le probleme

Le script `artifacts.js` est charge sur TOUTES les pages (y compris `/admin`) et ecrase le contenu du dashboard.

---

## Partie 2: Le Piege de la Fixation Fonctionnelle

### Qu'est-ce que la fixation fonctionnelle?

C'est un biais cognitif ou on reste bloque sur une approche de resolution meme si elle ne fonctionne pas.

### Tentatives qui n'ont PAS marche

| Tentative | Temps | Pourquoi ca n'a pas marche |
|-----------|-------|---------------------------|
| IIFE avec early return | 30 min | Script quand meme parse |
| Verification pathname | 45 min | Race condition avec HTMX |
| CSS z-index | 20 min | Ne resout pas l'ecrasement DOM |
| Blocage API | 15 min | Casse la page (reponse vide) |
| **Total** | **~2h** | - |

### La mauvaise question

> "Comment empecher ce script de s'executer sur /admin?"

### La bonne question

> "Pourquoi ce script est-il charge sur /admin en premier lieu?"

---

## Partie 3: Ta Mission

### Objectif

Empecher le script `artifacts.js` de s'executer sur les pages admin.

### Options de correction

| Option | Methode | Efficacite |
|--------|---------|------------|
| A | Condition dans le script | Faible |
| B | Condition dans le template | Elevee |
| C | Scripts separes par section | Tres elevee |

### Indices

<details>
<summary>Indice 1: Ou est le vrai probleme?</summary>

Le probleme n'est pas dans `artifacts.js`.
Le probleme est dans `base.html` qui charge le script partout.

</details>

<details>
<summary>Indice 2: Condition Jinja</summary>

```jinja
{% if condition %}
<script src="..."></script>
{% endif %}
```

</details>

<details>
<summary>Indice 3: Verifier l'URL en Jinja</summary>

```jinja
{% if not request.url.path.startswith('/admin') %}
    <!-- Charger le script seulement hors admin -->
{% endif %}
```

</details>

---

## Partie 4: Corrige (Solution Complete)

### Solution: Chargement conditionnel (2 lignes!)

**Fichier**: `templates/base.html`

```jinja
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}App{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}

    <script src="/static/js/main.js"></script>

    {# SOLUTION: Ne charger artifacts.js que hors admin #}
    {% if not request.url.path.startswith('/admin') %}
    <script src="/static/js/artifacts.js"></script>
    {% endif %}
</body>
</html>
```

**Temps de correction**: 30 secondes

**Pourquoi ca marche**: Pas de script = pas de probleme. Simple.

---

## Partie 5: Lecons Apprises

### 1. Eliminer plutot que gerer

```python
# MAUVAIS - Gerer le probleme
def artifacts_init():
    if window.location.pathname.startswith('/admin'):
        return  # N'execute pas
    # ... reste du code

# BON - Eliminer le probleme
# Ne pas charger le script du tout sur /admin
```

### 2. Se poser la bonne question

```
AVANT de corriger un bug, demandez-vous:
"Est-ce que ce code devrait exister ici en premier lieu?"
```

### 3. Prendre du recul

Apres 30 minutes sans progres:
1. Arretez
2. Expliquez le probleme a quelqu'un (ou au canard en plastique)
3. Reformulez la question
4. Cherchez une solution plus simple

### 4. La simplicite gagne toujours

| Approche complexe | Approche simple |
|-------------------|-----------------|
| IIFE, early return, conditions multiples | Une condition Jinja |
| 2+ heures de debug | 30 secondes |
| Code fragile | Code robuste |

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Qu'est-ce que la fixation fonctionnelle?

<details>
<summary>Reponse</summary>
Un biais cognitif ou on reste bloque sur une approche de resolution meme si elle ne fonctionne pas. On continue a chercher dans la meme direction au lieu de remettre en question l'approche.
</details>

### Question 2
Pourquoi la solution "condition dans le script" est-elle moins bonne?

<details>
<summary>Reponse</summary>
- Le script est quand meme telecharge et parse par le navigateur
- Consomme de la bande passante et du CPU inutilement
- Le code reste present, meme s'il ne s'execute pas
- Plus de complexite a maintenir
</details>

### Question 3
Quelle question devrait-on se poser avant de debugger?

<details>
<summary>Reponse</summary>
"Est-ce que ce code devrait exister ici en premier lieu?"

Souvent, la meilleure solution n'est pas de gerer un probleme, mais de l'eliminer a la source.
</details>

---

## Partie 7: Patterns Anti-Bug

### Pattern: Scripts par section

```html
<!-- base.html -->
<script src="/static/js/main.js"></script>
{% block scripts %}{% endblock %}

<!-- admin/base.html -->
{% block scripts %}
<script src="/static/js/admin.js"></script>
{% endblock %}

<!-- pages/artifacts.html -->
{% block scripts %}
<script src="/static/js/artifacts.js"></script>
{% endblock %}
```

### Pattern: Chargement conditionnel avance

```jinja
{# Scripts specifiques par section #}
{% set section = request.url.path.split('/')[1] if '/' in request.url.path else '' %}

{% if section == 'admin' %}
<script src="/static/js/admin.js"></script>
{% elif section == 'artifacts' %}
<script src="/static/js/artifacts.js"></script>
{% endif %}
```

### Pattern: Data attributes

```html
<body data-page="{{ page_name }}">

<script>
const page = document.body.dataset.page;
if (page === 'artifacts') {
    loadArtifactsModule();
}
</script>
```

---

## Ressources Supplementaires

- [Fixation Fonctionnelle (Wikipedia)](https://fr.wikipedia.org/wiki/Fixation_fonctionnelle)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- [The XY Problem](https://xyproblem.info/)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
