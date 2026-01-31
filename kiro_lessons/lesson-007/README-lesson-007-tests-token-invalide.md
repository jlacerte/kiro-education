# Cours 007: Tests - Token d'Authentification Invalide

## Niveau: Intermediaire

## Duree estimee: 25-35 minutes

## Prerequis

- Bases de Python
- Notions de tests unitaires
- Comprendre l'authentification par token

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur une API avec authentification. Les tests existent mais ils echouent mysterieusement avec des erreurs 401 (Non autorise).

### Code problematique

**Fichier**: `tests/api/test_admin.py`

```python
class TestAdminAPI:
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        self.auth_headers = {"Authorization": "Bearer test-token"}

    def test_get_metrics(self):
        response = requests.get(
            f"{self.base_url}/api/admin/metrics",
            headers=self.auth_headers
        )
        assert response.status_code == 200  # ECHOUE! 401 Unauthorized
```

### Le probleme

```bash
$ pytest tests/api/test_admin.py -v
FAILED test_get_metrics - AssertionError: assert 401 == 200
```

Le token `test-token` n'existe pas dans la configuration!

---

## Partie 2: Ta Mission

### Objectif

Corriger les tests pour qu'ils utilisent une authentification valide.

### Options de correction

| Option | Methode | Quand l'utiliser |
|--------|---------|------------------|
| A | Token valide hardcode | Quick fix, dev local |
| B | Variable d'environnement | CI/CD, multi-environnement |
| C | Mock de l'auth | Tests unitaires isoles |
| D | Fixture pytest | Tests d'integration |

### Questions a se poser

1. Les tests doivent-ils appeler la vraie API?
2. Faut-il tester l'authentification ou la fonctionnalite?
3. Comment gerer les tokens dans CI/CD?

### Indices

<details>
<summary>Indice 1: Trouver le vrai token</summary>

Cherche dans la configuration du projet:

```bash
# Dans le code
grep -r "ADMIN_TOKEN\|admin.*token" src/ --include="*.py"

# Dans les fichiers de config
cat .env
cat config.py
```

</details>

<details>
<summary>Indice 2: Variable d'environnement</summary>

```python
import os

# Au lieu d'un token hardcode:
token = os.getenv("TEST_ADMIN_TOKEN", "fallback-token")
```

</details>

<details>
<summary>Indice 3: Mocker l'authentification</summary>

```python
from unittest.mock import patch

@patch('src.api.routes.admin.verify_token')
def test_endpoint(mock_verify):
    mock_verify.return_value = {"user": "test"}
    # Le test n'a plus besoin d'un vrai token
```

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Comprendre le probleme

```bash
python exercice.py
```

L'analyseur va montrer pourquoi les tests echouent.

### Etape 2: Choisir une solution

- Tests d'integration? -> Option B (env var) ou D (fixture)
- Tests unitaires? -> Option C (mock)
- Quick fix? -> Option A (token valide)

### Etape 3: Implementer

Modifie `exercice.py` pour corriger le probleme.

---

## Partie 4: Corrige (Solutions Completes)

### Option A: Token valide (Quick fix)

```python
class TestAdminAPI:
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        # Token qui existe vraiment dans la config
        self.auth_headers = {"Authorization": "Bearer admin-token-hackathon2026"}
```

**Avantages**: Simple, rapide
**Inconvenients**: Token hardcode, pas flexible

### Option B: Variable d'environnement (Recommande)

```python
import os

class TestAdminAPI:
    def setup_method(self):
        self.base_url = os.getenv("TEST_API_URL", "http://localhost:8000")
        token = os.getenv("TEST_ADMIN_TOKEN", "admin-token-hackathon2026")
        self.auth_headers = {"Authorization": f"Bearer {token}"}
```

**Configuration CI/CD**:
```yaml
# .github/workflows/test.yml
env:
  TEST_ADMIN_TOKEN: ${{ secrets.ADMIN_TOKEN }}
```

### Option C: Mock (Best practice pour unit tests)

```python
from unittest.mock import patch, MagicMock

class TestAdminAPI:
    @patch('src.api.routes.admin.get_admin_user')
    def test_get_metrics(self, mock_auth):
        # Mock retourne un admin valide
        mock_auth.return_value = "test_admin"

        response = requests.get(
            f"{self.base_url}/api/admin/metrics",
            headers={"Authorization": "Bearer any-token"}
        )

        assert response.status_code == 200
```

**Avantages**: Tests isoles, rapides, pas besoin de vraie auth
**Inconvenients**: Ne teste pas l'auth reelle

### Option D: Fixture pytest (Recommande pour integration)

**Fichier**: `tests/conftest.py`

```python
import pytest
import os

@pytest.fixture
def admin_headers():
    """Headers d'authentification admin."""
    token = os.getenv("TEST_ADMIN_TOKEN", "admin-token-hackathon2026")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def api_url():
    """URL de base de l'API."""
    return os.getenv("TEST_API_URL", "http://localhost:8000")
```

**Fichier**: `tests/api/test_admin.py`

```python
def test_get_metrics(api_url, admin_headers):
    response = requests.get(
        f"{api_url}/api/admin/metrics",
        headers=admin_headers
    )
    assert response.status_code == 200
```

---

## Partie 5: Lecons Apprises

### 1. Ne jamais inventer de tokens

```python
# MAUVAIS - Token invente
headers = {"Authorization": "Bearer test-token"}

# BON - Token de la config
headers = {"Authorization": f"Bearer {os.getenv('ADMIN_TOKEN')}"}
```

### 2. Separer tests unitaires et integration

| Type | Auth | Base de donnees | Vitesse |
|------|------|-----------------|---------|
| Unitaire | Mockee | Mockee | Rapide |
| Integration | Reelle | Reelle | Lent |

### 3. Configuration par environnement

```python
# tests/conftest.py
import os

# Defaut pour dev local, override en CI
API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("TEST_ADMIN_TOKEN", "dev-token")
```

### 4. Ne pas commiter les vrais tokens

```gitignore
# .gitignore
.env
.env.test
secrets.json
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi le test echouait avec une erreur 401?

<details>
<summary>Reponse</summary>
Le token `test-token` n'existait pas dans la configuration du serveur.
L'API rejette les tokens invalides avec un code 401 (Unauthorized).
</details>

### Question 2
Quelle est la difference entre mocker l'auth et utiliser un vrai token?

<details>
<summary>Reponse</summary>
- **Mock**: Le test ne verifie PAS que l'authentification fonctionne, seulement la logique metier
- **Vrai token**: Le test verifie le flux complet, y compris l'authentification

Les deux approches sont valides pour des objectifs differents.
</details>

### Question 3
Comment gerer les tokens dans un pipeline CI/CD?

<details>
<summary>Reponse</summary>
Utiliser des secrets d'environnement:

```yaml
# GitHub Actions
env:
  TEST_ADMIN_TOKEN: ${{ secrets.ADMIN_TOKEN }}

# GitLab CI
variables:
  TEST_ADMIN_TOKEN: $ADMIN_TOKEN
```

Jamais de tokens en clair dans le code ou les fichiers YAML commites.
</details>

---

## Partie 7: Patterns de Tests

### Pattern AAA (Arrange, Act, Assert)

```python
def test_get_metrics(admin_headers):
    # Arrange
    url = "http://localhost:8000/api/admin/metrics"

    # Act
    response = requests.get(url, headers=admin_headers)

    # Assert
    assert response.status_code == 200
    assert "cpu_usage" in response.json()
```

### Pattern Given-When-Then

```python
def test_unauthorized_access():
    # Given: pas de token
    headers = {}

    # When: appel de l'API
    response = requests.get(url, headers=headers)

    # Then: rejet avec 401
    assert response.status_code == 401
```

---

## Ressources Supplementaires

- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [12 Factor App - Config](https://12factor.net/config)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
