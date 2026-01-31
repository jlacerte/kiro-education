"""
Cours 007: Tests - Token d'Authentification Invalide
=====================================================
CORRIGE - Solution Complete

Ce fichier montre les tests CORRIGES avec un token valide.
Compare avec exercice.py pour voir la difference.
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional


# ============================================================================
# SIMULATION DU SERVEUR (identique)
# ============================================================================

VALID_TOKENS = {
    "admin-token-hackathon2026": {"user": "admin", "role": "admin"},
    "user-token-12345": {"user": "user1", "role": "user"},
}


@dataclass
class MockResponse:
    status_code: int
    data: Optional[Dict] = None

    def json(self):
        return self.data or {}


def mock_api_request(endpoint: str, headers: Dict) -> MockResponse:
    auth_header = headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return MockResponse(status_code=401, data={"error": "Missing token"})

    token = auth_header.replace("Bearer ", "")

    if token not in VALID_TOKENS:
        return MockResponse(status_code=401, data={"error": f"Invalid token"})

    if endpoint == "/api/admin/metrics":
        return MockResponse(status_code=200, data={
            "cpu_usage": 45.2, "memory_usage": 62.1, "active_users": 128
        })
    elif endpoint == "/api/admin/content":
        return MockResponse(status_code=200, data={"items": [], "total": 0})

    return MockResponse(status_code=404)


# ============================================================================
# TESTS CORRIGES
# ============================================================================

class TestAdminAPI:
    """Tests pour l'API admin - VERSION CORRIGEE."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.base_url = "http://localhost:8000"

        # =============================================
        # CORRECTION: Utiliser un token valide
        # Option B: Variable d'environnement (recommande)
        # =============================================
        token = os.getenv("TEST_ADMIN_TOKEN", "admin-token-hackathon2026")
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_get_metrics(self) -> bool:
        """Test de recuperation des metriques."""
        response = mock_api_request(
            "/api/admin/metrics",
            headers=self.auth_headers
        )

        if response.status_code != 200:
            print(f"  ERREUR: Status {response.status_code}")
            return False

        data = response.json()
        if "cpu_usage" not in data:
            print("  ERREUR: cpu_usage manquant")
            return False

        return True

    def test_get_content(self) -> bool:
        """Test de recuperation du contenu."""
        response = mock_api_request(
            "/api/admin/content",
            headers=self.auth_headers
        )
        return response.status_code == 200

    def test_no_auth(self) -> bool:
        """Test sans authentification (doit echouer avec 401)."""
        response = mock_api_request("/api/admin/metrics", headers={})
        return response.status_code == 401


# ============================================================================
# EXEMPLE AVEC FIXTURE PYTEST
# ============================================================================

def example_pytest_fixture():
    """Exemple de fixture pytest pour l'authentification."""

    print("""
# tests/conftest.py
import pytest
import os

@pytest.fixture
def admin_headers():
    '''Headers d'authentification admin.'''
    token = os.getenv("TEST_ADMIN_TOKEN", "admin-token-hackathon2026")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def api_url():
    '''URL de base de l'API.'''
    return os.getenv("TEST_API_URL", "http://localhost:8000")


# tests/api/test_admin.py
def test_get_metrics(api_url, admin_headers):
    '''Utilise les fixtures automatiquement.'''
    response = requests.get(
        f"{api_url}/api/admin/metrics",
        headers=admin_headers
    )
    assert response.status_code == 200
""")


# ============================================================================
# EXEMPLE AVEC MOCK
# ============================================================================

def example_mock_auth():
    """Exemple de mock pour l'authentification."""

    print("""
# tests/api/test_admin.py
from unittest.mock import patch

class TestAdminAPI:
    @patch('src.api.routes.admin.get_admin_user')
    def test_get_metrics_mocked(self, mock_auth):
        '''Test avec authentification mockee.'''
        # Le mock retourne toujours un admin valide
        mock_auth.return_value = "test_admin"

        response = requests.get(
            "http://localhost:8000/api/admin/metrics",
            headers={"Authorization": "Bearer any-token"}
        )

        assert response.status_code == 200
        mock_auth.assert_called_once()
""")


# ============================================================================
# EXECUTION
# ============================================================================

def run_tests():
    """Execute les tests corriges."""

    print("="*60)
    print("COURS 007 - CORRIGE - Tests avec Token Valide")
    print("="*60)
    print()

    test_suite = TestAdminAPI()
    test_suite.setup_method()

    print("Token utilise (corrige):")
    print("-" * 40)
    print(f"  {test_suite.auth_headers.get('Authorization', 'None')}")
    print()

    results = []

    print("Test 1: test_get_metrics")
    passed = test_suite.test_get_metrics()
    results.append(passed)
    print(f"  {'✓ PASSE' if passed else '✗ ECHOUE'}")

    print("Test 2: test_get_content")
    passed = test_suite.test_get_content()
    results.append(passed)
    print(f"  {'✓ PASSE' if passed else '✗ ECHOUE'}")

    print("Test 3: test_no_auth")
    passed = test_suite.test_no_auth()
    results.append(passed)
    print(f"  {'✓ PASSE' if passed else '✗ ECHOUE'}")

    print()
    print("="*60)
    print(f"RESULTAT: {sum(results)}/{len(results)} tests passes")
    print("="*60)

    if all(results):
        print()
        print("✅ TOUS LES TESTS PASSENT!")

    return all(results)


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Le token "test-token" n'existait pas dans VALID_TOKENS.
Les tests echouaient avec 401 Unauthorized.

CORRECTION:
-----------
Utiliser un token qui existe vraiment:

    # AVANT (invalide)
    self.auth_headers = {"Authorization": "Bearer test-token"}

    # APRES (valide)
    token = os.getenv("TEST_ADMIN_TOKEN", "admin-token-hackathon2026")
    self.auth_headers = {"Authorization": f"Bearer {token}"}

AVANTAGES DE LA VARIABLE D'ENVIRONNEMENT:
-----------------------------------------
1. Flexible: different token en dev/CI/prod
2. Securise: pas de token hardcode dans le code
3. Configurable: facile a changer sans modifier le code

CONFIGURATION CI/CD:
--------------------
GitHub Actions:
    env:
      TEST_ADMIN_TOKEN: ${{ secrets.ADMIN_TOKEN }}

GitLab CI:
    variables:
      TEST_ADMIN_TOKEN: $ADMIN_TOKEN

============================================================
""")


if __name__ == "__main__":
    run_tests()
    print()
    show_explanation()
    print()
    print("="*60)
    print("EXEMPLES SUPPLEMENTAIRES")
    print("="*60)
    example_pytest_fixture()
    example_mock_auth()
