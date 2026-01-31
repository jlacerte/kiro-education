# Cours 006: Clean Code - Duplication de Fichiers

## Niveau: Debutant

## Duree estimee: 20-30 minutes

## Prerequis

- Bases de Python
- Notions de gestion de projet

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur un projet et tu remarques deux fichiers avec des noms similaires:

```
src/api/routes/
├── admin.py
└── admin_secure.py
```

Lequel utiliser? Lequel modifier? Sont-ils differents?

### Situation decouverte

En ouvrant les deux fichiers, tu constates:
- `admin.py` - 150 lignes, utilise dans `main.py`
- `admin_secure.py` - 155 lignes, tres similaire, mais NON utilise

### Le probleme

```python
# main.py
from src.api.routes import admin  # <- admin.py est utilise
# admin_secure.py n'est JAMAIS importe!
```

---

## Partie 2: Ta Mission

### Objectif

1. Identifier quel fichier est utilise
2. Determiner si l'autre contient des ameliorations
3. Fusionner si necessaire
4. Supprimer le fichier en double

### Questions a se poser

1. Quel fichier est reellement importe/utilise?
2. Pourquoi le deuxieme fichier existe-t-il?
3. Y a-t-il des differences importantes entre les deux?
4. Comment eviter cette situation a l'avenir?

### Indices

<details>
<summary>Indice 1: Trouver quel fichier est utilise</summary>

```bash
# Chercher les imports de admin_secure
grep -r "admin_secure" src/ --include="*.py"

# Si aucun resultat: admin_secure.py n'est PAS utilise!

# Chercher les imports de admin
grep -r "from.*admin import\|import admin" src/ --include="*.py"
```

</details>

<details>
<summary>Indice 2: Comparer les fichiers</summary>

```bash
# Voir les differences
diff admin.py admin_secure.py

# Ou avec un outil visuel
code --diff admin.py admin_secure.py
```

</details>

<details>
<summary>Indice 3: Origine probable</summary>

`admin_secure.py` est probablement:
- Une tentative de correction non terminee
- Une copie de backup oubliee
- Un fichier de travail jamais merge

Le suffixe `_secure` suggere une amelioration de securite
qui n'a jamais ete appliquee au fichier principal.

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Lancer l'analyseur

```bash
python exercice.py
```

L'analyseur va detecter les fichiers dupliques.

### Etape 2: Analyser les differences

L'outil va montrer:
- Quels fichiers sont similaires
- Lequel est reellement utilise
- Les differences entre eux

### Etape 3: Decider de l'action

- **Fusionner**: Si `admin_secure.py` a des ameliorations
- **Supprimer**: Si c'est juste une copie obsolete

---

## Partie 4: Corrige (Solution Complete)

### Etape 1: Verifier l'utilisation

```bash
$ grep -r "admin_secure" src/ --include="*.py"
# (aucun resultat)

$ grep -r "from.*routes.*admin" src/ --include="*.py"
main.py:from src.api.routes import admin
```

**Conclusion**: `admin_secure.py` n'est PAS utilise.

### Etape 2: Comparer les fichiers

```bash
$ diff admin.py admin_secure.py
32c32
< admin_token = os.getenv("ADMIN_TOKEN", "dev-token")
---
> admin_token = os.getenv("ADMIN_TOKEN")
> if not admin_token:
>     raise ValueError("ADMIN_TOKEN required")
```

**Conclusion**: `admin_secure.py` a une meilleure gestion des tokens!

### Etape 3: Fusionner les ameliorations

```python
# Dans admin.py, appliquer la correction de admin_secure.py:

# Avant (admin.py)
admin_token = os.getenv("ADMIN_TOKEN", "dev-token")

# Apres (fusion)
admin_token = os.getenv("ADMIN_TOKEN")
if not admin_token:
    raise ValueError("ADMIN_TOKEN required")
```

### Etape 4: Supprimer le doublon

```bash
git rm src/api/routes/admin_secure.py
git commit -m "fix: Remove duplicate admin_secure.py, merged improvements into admin.py"
```

---

## Partie 5: Lecons Apprises

### 1. Principe DRY (Don't Repeat Yourself)

```
MAUVAIS:
├── admin.py
├── admin_secure.py    # Doublon!
├── admin_backup.py    # Doublon!
└── admin_v2.py        # Doublon!

BON:
├── admin.py           # Un seul fichier
└── (utiliser git pour l'historique)
```

### 2. Utiliser Git au lieu de copies

```bash
# Au lieu de creer admin_backup.py:
git stash           # Sauvegarder temporairement
git branch feature  # Creer une branche

# Au lieu de admin_v2.py:
git log admin.py    # Voir l'historique
git checkout abc123 -- admin.py  # Revenir a une version
```

### 3. Detecter les doublons

```bash
# Trouver les fichiers similaires par nom
find . -name "*.py" | xargs -I {} basename {} | sort | uniq -d

# Trouver les fichiers similaires par contenu
fdupes -r src/

# Ou en Python
import hashlib
# Comparer les hash des fichiers
```

### 4. Convention de nommage

| Suffixe | Signification | Action |
|---------|---------------|--------|
| `_backup` | Copie de sauvegarde | Supprimer, utiliser git |
| `_old` | Ancienne version | Supprimer, utiliser git |
| `_v2` | Nouvelle version | Fusionner et renommer |
| `_secure` | Version securisee | Fusionner dans l'original |
| `_test` | Pour les tests | OK si dans `/tests/` |

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Comment savoir si un fichier Python est utilise dans le projet?

<details>
<summary>Reponse</summary>

```bash
# Chercher les imports
grep -r "import filename" src/ --include="*.py"
grep -r "from.*filename" src/ --include="*.py"

# Si aucun resultat, le fichier n'est probablement pas utilise.
```

</details>

### Question 2
Pourquoi la duplication de fichiers est-elle problematique?

<details>
<summary>Reponse</summary>

1. **Confusion**: Quel fichier modifier?
2. **Divergence**: Les copies evoluent differemment
3. **Bugs caches**: Corrections faites dans un seul fichier
4. **Maintenance**: Double effort de maintenance
5. **Espace**: Occupe de l'espace inutilement
</details>

### Question 3
Quelle est la meilleure alternative aux copies de fichiers?

<details>
<summary>Reponse</summary>

Utiliser Git:
- `git branch` pour les fonctionnalites en cours
- `git stash` pour les modifications temporaires
- `git log` pour voir l'historique
- `git checkout` pour revenir a une version

Git conserve TOUT l'historique sans creer de doublons.
</details>

---

## Partie 7: Prevention

### Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: no-duplicate-files
        name: Check for duplicate file patterns
        entry: bash -c 'find . -name "*_backup*" -o -name "*_old*" -o -name "*_copy*" | grep -q . && exit 1 || exit 0'
        language: system
```

### Script de detection

```python
#!/usr/bin/env python3
"""Detecte les fichiers potentiellement dupliques."""

import os
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    '_backup', '_old', '_copy', '_v2', '_new',
    '_temp', '_test', '_secure', '_fixed'
]

def find_duplicates(directory):
    duplicates = []
    for path in Path(directory).rglob('*.py'):
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in path.stem:
                duplicates.append(path)
    return duplicates

if __name__ == '__main__':
    dupes = find_duplicates('src/')
    if dupes:
        print("Fichiers suspects trouves:")
        for d in dupes:
            print(f"  - {d}")
    else:
        print("Aucun doublon detecte.")
```

---

## Ressources Supplementaires

- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [Git Branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)
- [fdupes - Find duplicate files](https://github.com/adrianlopezroche/fdupes)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
