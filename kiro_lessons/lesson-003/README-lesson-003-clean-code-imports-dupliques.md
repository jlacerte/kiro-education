# Cours 003: Clean Code - Imports Dupliques

## Niveau: Debutant

## Duree estimee: 15-20 minutes

## Prerequis

- Bases de Python
- Savoir ce qu'est un import

---

## Partie 1: Enonce du Probleme

### Contexte

Tu fais une revue de code et tu remarques que le fichier est un peu desorganise. En regardant de plus pres, tu vois quelque chose de suspect...

### Le code problematique

**Fichier**: `admin_service.py`

```python
# Ligne 1-15
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# ... du code ...

# Ligne 20-25
import sys
import os
sys.path.append(str(Path(__file__).parent.parent))

# ... encore du code ...
```

### Les problemes

1. **`import os`** apparait deux fois (lignes 1 et 21)
2. **`import sys`** apparait deux fois (lignes 2 et 20)
3. Les imports sont disperses dans le fichier au lieu d'etre regroupes

---

## Partie 2: Ta Mission

### Objectif

Nettoyer le fichier en:
1. Supprimant les imports dupliques
2. Regroupant tous les imports en haut du fichier
3. Organisant les imports selon les conventions Python

### Convention PEP 8 pour les imports

```python
# 1. Imports de la bibliotheque standard
import os
import sys
from datetime import datetime

# 2. Imports de bibliotheques tierces
import requests
from fastapi import FastAPI

# 3. Imports locaux
from .models import User
from ..utils import helpers
```

### Questions a te poser

1. Pourquoi les imports dupliques sont-ils un probleme?
2. Comment Python gere-t-il un import duplique?
3. Quel outil peut detecter automatiquement ces problemes?

### Indices

<details>
<summary>Indice 1: Impact des imports dupliques</summary>

Python ne charge un module qu'une seule fois (cache dans `sys.modules`).
Les imports dupliques ne causent pas d'erreur mais:
- Reduisent la lisibilite
- Indiquent un code mal organise
- Peuvent cacher des problemes de dependances circulaires

</details>

<details>
<summary>Indice 2: Outils de detection</summary>

Plusieurs outils peuvent detecter les imports dupliques:
- `pylint` avec le check `duplicate-imports`
- `flake8` avec le plugin `flake8-import-order`
- `isort` pour trier et dedupliquer automatiquement

```bash
pip install isort
isort --check-only --diff mon_fichier.py
```

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Lancer l'analyseur

```bash
python exercice.py
```

Tu verras les imports dupliques detectes.

### Etape 2: Corriger le code

Modifie le code dans `exercice.py` pour:
1. Supprimer les doublons
2. Regrouper les imports en haut
3. Suivre l'ordre PEP 8

### Etape 3: Verifier

Relance l'analyseur jusqu'a ce qu'il passe.

---

## Partie 4: Corrige (Solution Complete)

### Le probleme

Les imports etaient dupliques et disperses dans le fichier:

```python
# En haut du fichier
import os
import sys

# Plus bas dans le fichier
import sys  # DUPLIQUE!
import os   # DUPLIQUE!
sys.path.append(...)
```

### La solution

Regrouper tous les imports en haut et supprimer les doublons:

```python
# Bibliotheque standard
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Modifier sys.path APRES l'import unique
sys.path.append(str(Path(__file__).parent.parent))

# Bibliotheques tierces
import sqlite3

# Imports locaux (apres sys.path.append)
from models import ContentFilter, ContentItem
```

### Diff de la correction

```diff
  import os
  import sys
  import json
  from datetime import datetime
  from pathlib import Path

- # ... du code ...
-
- import sys  # SUPPRIME
- import os   # SUPPRIME
  sys.path.append(str(Path(__file__).parent.parent))
```

---

## Partie 5: Lecons Apprises

### 1. Un seul bloc d'imports en haut

```python
# BON
import os
import sys
# tout le reste du code

# MAUVAIS
import os
# du code
import sys  # Import disperse!
```

### 2. Ordre des imports (PEP 8)

```python
# 1. Standard library
import os
import sys

# 2. Third party
import requests
import numpy

# 3. Local
from . import utils
```

### 3. Outils automatiques

```bash
# Trier et dedupliquer automatiquement
isort mon_fichier.py

# Verifier sans modifier
isort --check-only --diff mon_fichier.py

# Configuration dans pyproject.toml
[tool.isort]
profile = "black"
```

### 4. Pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Python charge-t-il un module plusieurs fois s'il est importe deux fois?

<details>
<summary>Reponse</summary>
Non. Python cache les modules dans `sys.modules`. Un import duplique ne recharge pas le module, il recupere juste la reference du cache.
</details>

### Question 2
Dans quel ordre doit-on organiser les imports selon PEP 8?

<details>
<summary>Reponse</summary>
1. Bibliotheque standard (os, sys, json...)
2. Bibliotheques tierces (requests, numpy...)
3. Imports locaux (from . import ...)

Avec une ligne vide entre chaque groupe.
</details>

### Question 3
Quel outil peut corriger automatiquement l'ordre des imports?

<details>
<summary>Reponse</summary>
`isort` - Il trie, regroupe et deduplique les imports automatiquement.

```bash
pip install isort
isort mon_fichier.py
```
</details>

---

## Ressources Supplementaires

- [PEP 8 - Imports](https://peps.python.org/pep-0008/#imports)
- [isort documentation](https://pycqa.github.io/isort/)
- [Python Import System](https://docs.python.org/3/reference/import.html)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
