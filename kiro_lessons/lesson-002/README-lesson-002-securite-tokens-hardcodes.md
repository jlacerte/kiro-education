# Cours 002: Securite - Tokens Hardcodes

## Niveau: Debutant

## Duree estimee: 30-45 minutes

## Prerequis

- Bases de Python
- Comprendre ce qu'est une variable d'environnement
- Notions basiques de securite web

---

## Partie 1: Enonce du Probleme

### Contexte

Tu fais une revue de code sur une application web. Un collegue a commit du code pour l'authentification admin. Tu remarques quelque chose de suspect...

### Le rapport de securite

> **ALERTE SECURITE**: Des tokens d'authentification ont ete trouves en clair dans le code source. Toute personne avec acces au repository peut s'authentifier comme administrateur.

### Code suspect

**Fichier**: `admin_auth.py`

```python
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_admin_password():
    """Recupere le mot de passe admin"""
    return os.getenv("ADMIN_PASSWORD", "hackathon2026")  # Fallback "securise"

def get_admin_token():
    """Recupere le token admin"""
    return os.getenv("ADMIN_TOKEN", "dev-token-blade-runner")  # Pour le dev

async def verify_admin(token: str = Depends(security)) -> str:
    """Verifie si l'utilisateur est admin"""
    valid_token = get_admin_token()

    if token.credentials != valid_token:
        raise HTTPException(status_code=403, detail="Access denied")

    return "admin"
```

**Fichier**: `admin.js` (frontend)

```javascript
function getAdminToken() {
    const storedToken = localStorage.getItem('admin_token');
    return storedToken || 'admin-secure-token-2026';  // Fallback pour debug
}
```

### Les problemes

1. **Mot de passe en fallback**: `"hackathon2026"` est visible dans le code
2. **Token en fallback**: `"dev-token-blade-runner"` est visible dans le code
3. **Token JS expose**: `'admin-secure-token-2026'` est dans le JavaScript client

---

## Partie 2: Ta Mission

### Objectif

Corriger le code pour eliminer tous les secrets hardcodes.

### Regles de securite a appliquer

1. **JAMAIS de fallback pour les secrets** - Si la variable d'environnement n'existe pas, l'application doit refuser de demarrer
2. **Pas de secrets dans le frontend** - Le JavaScript est visible par tous
3. **Messages d'erreur explicites** - Dire clairement quelle config manque

### Questions a te poser

1. Que se passe-t-il si quelqu'un clone le repo et lance l'app sans configurer les variables?
2. Pourquoi un fallback "pour le dev" est-il dangereux?
3. Comment forcer les developpeurs a configurer les secrets?

### Indices

<details>
<summary>Indice 1: Eliminer les fallbacks</summary>

Au lieu de:
```python
token = os.getenv("TOKEN", "default-value")
```

Faire:
```python
token = os.getenv("TOKEN")
if not token:
    raise ValueError("TOKEN environment variable is required")
```

</details>

<details>
<summary>Indice 2: Validation au demarrage</summary>

Creer une fonction qui valide TOUTES les variables requises au demarrage:

```python
def validate_config():
    required = ["ADMIN_TOKEN", "ADMIN_PASSWORD", "SECRET_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required env vars: {missing}")
```

</details>

<details>
<summary>Indice 3: Frontend sans secrets</summary>

Le frontend ne devrait JAMAIS contenir de tokens. L'authentification doit:
1. Envoyer les credentials au backend
2. Le backend valide et retourne un token de session
3. Le frontend stocke ce token temporaire (pas un secret permanent)

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Identifier les vulnerabilites

Lance le fichier d'exercice:

```bash
python exercice.py
```

Tu verras les tests de securite echouer.

### Etape 2: Corriger le code

Modifie `exercice.py` pour:
1. Retirer tous les fallbacks de secrets
2. Lever une erreur si les variables manquent
3. Retirer le token hardcode du "frontend"

### Etape 3: Tester avec des variables d'environnement

```bash
# Linux/Mac
export ADMIN_TOKEN="mon-token-secret"
python exercice.py

# Windows PowerShell
$env:ADMIN_TOKEN="mon-token-secret"
python exercice.py
```

---

## Partie 4: Corrige (Solution Complete)

### Le probleme

Les fallbacks permettent a l'application de fonctionner SANS configuration securisee.
Un attaquant peut simplement utiliser les valeurs par defaut.

### La solution

```python
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict

security = HTTPBearer()

def get_admin_tokens() -> Dict[str, str]:
    """
    Recupere les tokens admin depuis les variables d'environnement.
    SANS FALLBACK - l'app refuse de demarrer si non configure.
    """
    admin_token = os.getenv("ADMIN_TOKEN")

    # SECURITE: Pas de fallback, erreur explicite
    if not admin_token:
        raise ValueError(
            "ADMIN_TOKEN environment variable is required. "
            "Set it before starting the application."
        )

    return {
        admin_token: "admin_user"
    }

async def verify_admin(token: str = Depends(security)) -> str:
    """
    Verifie l'authentification admin.
    Utilise les tokens configures par environnement.
    """
    if not token or not token.credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    # Recuperer les tokens valides (leve une erreur si non configure)
    admin_tokens = get_admin_tokens()

    if token.credentials not in admin_tokens:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin token"
        )

    return admin_tokens[token.credentials]
```

### Pour le frontend

```javascript
// CORRIGE: Pas de token hardcode
function getAdminToken() {
    const storedToken = localStorage.getItem('admin_token');

    if (!storedToken) {
        // Rediriger vers la page de login au lieu de fallback
        window.location.href = '/admin/login';
        return null;
    }

    return storedToken;
}
```

### Diff de la correction

```diff
- def get_admin_token():
-     return os.getenv("ADMIN_TOKEN", "dev-token-blade-runner")
+ def get_admin_tokens():
+     admin_token = os.getenv("ADMIN_TOKEN")
+     if not admin_token:
+         raise ValueError("ADMIN_TOKEN environment variable is required")
+     return {admin_token: "admin_user"}
```

---

## Partie 5: Lecons Apprises

### 1. Jamais de fallback pour les secrets

```python
# DANGEREUX
password = os.getenv("PASSWORD", "admin123")

# SECURISE
password = os.getenv("PASSWORD")
if not password:
    raise ValueError("PASSWORD is required")
```

### 2. Fail fast, fail loud

L'application doit refuser de demarrer si elle n'est pas configuree correctement.
Un crash au demarrage est BEAUCOUP mieux qu'une faille de securite en production.

### 3. Secrets != Code

| Appartient au CODE | Appartient a l'ENVIRONNEMENT |
|--------------------|------------------------------|
| Logique metier | Mots de passe |
| Structures de donnees | Tokens API |
| Algorithmes | Cles de chiffrement |
| Configuration par defaut (non-sensible) | URLs de base de donnees |

### 4. Le frontend est PUBLIC

Tout ce qui est dans le JavaScript peut etre lu par n'importe qui.
Les secrets doivent rester cote serveur.

### 5. Defense en profondeur

Meme si quelqu'un a acces au code source, il ne devrait pas pouvoir:
- Se connecter en production
- Acceder aux donnees sensibles
- Usurper un admin

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi `os.getenv("TOKEN", "default")` est dangereux pour un secret?

<details>
<summary>Reponse</summary>
Parce que "default" est visible dans le code source. Toute personne avec acces au code peut l'utiliser pour s'authentifier.
</details>

### Question 2
Que doit faire l'application si une variable d'environnement requise manque?

<details>
<summary>Reponse</summary>
Elle doit refuser de demarrer avec un message d'erreur clair. Exemple:
`raise ValueError("ADMIN_TOKEN environment variable is required")`
</details>

### Question 3
Pourquoi ne pas mettre de token dans le JavaScript frontend?

<details>
<summary>Reponse</summary>
Le JavaScript est envoye au navigateur et peut etre lu par n'importe qui (via View Source, DevTools, etc.). Les secrets doivent rester cote serveur.
</details>

### Question 4
Comment les developpeurs doivent-ils gerer les secrets en local?

<details>
<summary>Reponse</summary>
Utiliser un fichier `.env` (ajoute au `.gitignore`) ou des variables d'environnement systeme. Jamais de secrets dans le code.
</details>

---

## Partie 7: Bonnes Pratiques

### Fichier `.env.example`

Creer un fichier template sans les vraies valeurs:

```bash
# .env.example (commite dans git)
ADMIN_TOKEN=your-secret-token-here
ADMIN_PASSWORD=your-password-here
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Fichier `.gitignore`

```gitignore
# Ne jamais commiter les vrais secrets
.env
.env.local
.env.production
*.pem
*.key
```

### Validation au demarrage

```python
# config.py
import os
import sys

REQUIRED_ENV_VARS = [
    "ADMIN_TOKEN",
    "DATABASE_URL",
    "SECRET_KEY"
]

def validate_environment():
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nCopy .env.example to .env and fill in the values.")
        sys.exit(1)

# Appeler au demarrage de l'app
validate_environment()
```

---

## Ressources Supplementaires

- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12 Factor App: Config](https://12factor.net/config)
- [Python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Commit de Reference

```
Commit: (voir branche maitre-claude)
Message: fix(security): Remove hardcoded tokens, require env vars - Issue 002
Fichiers: src/api/routes/admin.py, static/js/admin.js
```

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
