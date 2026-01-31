"""
Cours 007: Tests - Token d'Authentification Invalide
=====================================================
EXERCICE - Code a corriger

Niveau: Intermediaire
Duree: 25-35 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule des tests avec un token invalide
2. Lance le script pour voir les tests echouer
3. Corrige le probleme d'authentification
4. Les tests doivent passer

Pour lancer:
    python exercice.py
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional
from unittest.mock import MagicMock


# ============================================================================
# SIMULATION DU SERVEUR
# ============================================================================

# Tokens valides configures sur le "serveur"
VALID_TOKENS = {
    "admin-token-hackathon2026": {"user": "admin", "role": "admin"},
    "user-token-12345": {"user": "user1", "role": "user"},
}


@dataclass
class MockResponse:
    """Simule une reponse HTTP."""
    status_code: int
    data: Optional[Dict] = None

    def json(self):
        return self.data or {}


def mock_api_request(endpoint: str, headers: Dict) -> MockResponse:
    """Simule une requete API avec authentification."""

    # Verifier le header Authorization
    auth_header = headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return MockResponse(status_code=401, data={"error": "Missing token"})

    token = auth_header.replace("Bearer ", "")

    if token not in VALID_TOKENS:
        return MockResponse(
            status_code=401,
            data={"error": f"Invalid token: {token}"}
        )

    # Token valide - retourner les donnees
    if endpoint == "/api/admin/metrics":
        return MockResponse(
            status_code=200,
            data={
                "cpu_usage": 45.2,
                "memory_usage": 62.1,
                "active_users": 128
            }
        )
    elif endpoint == "/api/admin/content":
        return MockResponse(
            status_code=200,
            data={"items": [], "total": 0}
        )

    return MockResponse(status_code=404, data={"error": "Not found"})


# ============================================================================
# TESTS AVEC TOKEN INVALIDE - A CORRIGER
# ============================================================================

class TestAdminAPI:
    """Tests pour l'API admin."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.base_url = "http://localhost:8000"

        # =============================================
        # BUG: Token invalide!
        # "test-token" n'existe pas dans VALID_TOKENS
        # =============================================
        self.auth_headers = {"Authorization": "Bearer test-token"}

    def test_get_metrics(self) -> bool:
        """Test de recuperation des metriques."""
        response = mock_api_request(
            "/api/admin/metrics",
            headers=self.auth_headers
        )

        if response.status_code != 200:
            print(f"  ERREUR: Status {response.status_code}")
            print(f"  Message: {response.json()}")
            return False

        data = response.json()
        if "cpu_usage" not in data:
            print("  ERREUR: cpu_usage manquant dans la reponse")
            return False

        return True

    def test_get_content(self) -> bool:
        """Test de recuperation du contenu."""
        response = mock_api_request(
            "/api/admin/content",
            headers=self.auth_headers
        )

        if response.status_code != 200:
            print(f"  ERREUR: Status {response.status_code}")
            print(f"  Message: {response.json()}")
            return False

        return True

    def test_no_auth(self) -> bool:
        """Test sans authentification (doit echouer)."""
        response = mock_api_request(
            "/api/admin/metrics",
            headers={}  # Pas de token
        )

        # Ce test DOIT retourner 401
        if response.status_code != 401:
            print(f"  ERREUR: Devrait etre 401, got {response.status_code}")
            return False

        return True


# ============================================================================
# EXECUTION DES TESTS
# ============================================================================

def run_tests():
    """Execute tous les tests et affiche les resultats."""

    print("="*60)
    print("COURS 007 - Tests avec Token Invalide")
    print("="*60)
    print()

    # Afficher les tokens valides (pour debug)
    print("Tokens valides configures:")
    print("-" * 40)
    for token in VALID_TOKENS:
        print(f"  - {token[:20]}...")
    print()

    # Instancier et executer les tests
    test_suite = TestAdminAPI()
    test_suite.setup_method()

    print("Token utilise dans les tests:")
    print("-" * 40)
    print(f"  {test_suite.auth_headers.get('Authorization', 'None')}")
    print()

    results = []

    # Test 1: Get Metrics
    print("Test 1: test_get_metrics")
    print("-" * 40)
    passed = test_suite.test_get_metrics()
    results.append(("test_get_metrics", passed))
    print(f"  {'✓ PASSE' if passed else '✗ ECHOUE'}")
    print()

    # Test 2: Get Content
    print("Test 2: test_get_content")
    print("-" * 40)
    passed = test_suite.test_get_content()
    results.append(("test_get_content", passed))
    print(f"  {'✓ PASSE' if passed else '✗ ECHOUE'}")
    print()

    # Test 3: No Auth (ce test devrait passer)
    print("Test 3: test_no_auth (devrait passer)")
    print("-" * 40)
    passed = test_suite.test_no_auth()
    results.append(("test_no_auth", passed))
    print(f"  {'✓ PASSE' if passed else '✗ ECHOUE'}")
    print()

    # Resume
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print("="*60)
    print(f"RESULTAT: {passed_count}/{total_count} tests passes")
    print("="*60)
    print()

    if passed_count < total_count:
        print("❌ TESTS ECHOUES!")
        print()
        print("PROBLEME:")
        print("-" * 40)
        print("  Le token 'test-token' n'existe pas dans VALID_TOKENS!")
        print()
        print("SOLUTIONS:")
        print("-" * 40)
        print("""
  Option A: Utiliser un token valide
  ----------------------------------
  self.auth_headers = {"Authorization": "Bearer admin-token-hackathon2026"}

  Option B: Variable d'environnement
  ----------------------------------
  token = os.getenv("TEST_ADMIN_TOKEN", "admin-token-hackathon2026")
  self.auth_headers = {"Authorization": f"Bearer {token}"}

  Option C: Mock l'authentification
  ---------------------------------
  Modifier mock_api_request() pour accepter tout token en mode test
""")
    else:
        print("✅ TOUS LES TESTS PASSENT!")
        print()
        print("L'authentification est correctement configuree.")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    run_tests()
