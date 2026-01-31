"""
Cours 002: Securite - Tokens Hardcodes
======================================
CORRIGE - Solution Complete

Ce fichier contient la version SECURISEE.
Compare avec ton exercice pour voir les differences.

Les corrections sont sur 3 fonctions:
- get_admin_password()
- get_admin_token()
- get_frontend_token()
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass


# ============================================================================
# SIMULATION FASTAPI (pour l'exercice)
# ============================================================================

@dataclass
class HTTPCredentials:
    """Simule les credentials HTTP Bearer"""
    credentials: str


class HTTPException(Exception):
    """Simule une exception HTTP"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


# ============================================================================
# CODE SECURISE
# ============================================================================

def get_admin_password() -> str:
    """
    Recupere le mot de passe admin depuis les variables d'environnement.

    SECURITE: Pas de fallback! Leve une erreur si non configure.

    Returns:
        str: Le mot de passe admin

    Raises:
        ValueError: Si ADMIN_PASSWORD n'est pas defini
    """
    # ========================================================
    # CORRECTION: Pas de deuxieme argument (pas de fallback)
    # ========================================================
    password = os.getenv("ADMIN_PASSWORD")

    if not password:
        raise ValueError(
            "ADMIN_PASSWORD environment variable is required. "
            "Set it before starting the application."
        )

    return password


def get_admin_token() -> str:
    """
    Recupere le token admin depuis les variables d'environnement.

    SECURITE: Pas de fallback! Leve une erreur si non configure.

    Returns:
        str: Le token admin

    Raises:
        ValueError: Si ADMIN_TOKEN n'est pas defini
    """
    # ========================================================
    # CORRECTION: Pas de deuxieme argument (pas de fallback)
    # ========================================================
    token = os.getenv("ADMIN_TOKEN")

    if not token:
        raise ValueError(
            "ADMIN_TOKEN environment variable is required. "
            "Set it before starting the application."
        )

    return token


def verify_admin(token: HTTPCredentials) -> str:
    """
    Verifie si le token est valide pour un admin.

    Args:
        token: Les credentials HTTP Bearer

    Returns:
        str: Le nom de l'utilisateur admin

    Raises:
        HTTPException: Si le token est invalide
        ValueError: Si ADMIN_TOKEN n'est pas configure
    """
    if not token or not token.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    # get_admin_token() leve ValueError si non configure
    valid_token = get_admin_token()

    if token.credentials != valid_token:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    return "admin_user"


def get_frontend_token() -> Optional[str]:
    """
    Simule le code JavaScript frontend SECURISE.

    SECURITE: Pas de token hardcode!
    Retourne None si pas de token stocke (doit rediriger vers login).

    Returns:
        Optional[str]: Le token stocke ou None
    """
    # ========================================================
    # CORRECTION: Pas de fallback! Retourne None si pas de token
    # ========================================================
    stored_token = None  # Simule localStorage.getItem('admin_token')

    # Si pas de token, retourner None (le frontend redirigera vers login)
    # Au lieu de: return stored_token or 'admin-secure-token-2026'
    return stored_token  # Peut etre None, c'est voulu!


# ============================================================================
# BONUS: Validation de configuration au demarrage
# ============================================================================

def validate_environment():
    """
    Valide que toutes les variables d'environnement requises sont definies.
    A appeler au demarrage de l'application.

    Raises:
        ValueError: Si des variables requises manquent
    """
    required_vars = [
        "ADMIN_TOKEN",
        "ADMIN_PASSWORD",
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Create a .env file or set them in your environment."
        )


# ============================================================================
# AUDIT DE SECURITE (identique a l'exercice)
# ============================================================================

def audit_security():
    """Execute un audit de securite sur le code."""

    print("="*60)
    print("COURS 002 - CORRIGE - Audit de Securite")
    print("="*60)
    print()

    vulnerabilities = []
    warnings = []
    passed = []

    # Test 1: Verifier qu'il n'y a pas de fallback pour ADMIN_PASSWORD
    print("Test 1: ADMIN_PASSWORD sans fallback")
    print("-" * 40)

    original_password = os.environ.pop("ADMIN_PASSWORD", None)

    try:
        result = get_admin_password()
        if result == "hackathon2026":
            print("✗ VULNERABILITE: Fallback 'hackathon2026' detecte!")
            vulnerabilities.append("ADMIN_PASSWORD a un fallback hardcode")
        elif result is not None and result != "":
            print("✗ VULNERABILITE: Un fallback existe!")
            vulnerabilities.append("ADMIN_PASSWORD retourne une valeur sans env var")
        else:
            print("✓ SECURISE: Pas de fallback")
            passed.append("ADMIN_PASSWORD")
    except (ValueError, RuntimeError) as e:
        print(f"✓ SECURISE: Leve une erreur sans env var")
        passed.append("ADMIN_PASSWORD")
    finally:
        if original_password:
            os.environ["ADMIN_PASSWORD"] = original_password
    print()

    # Test 2: Verifier qu'il n'y a pas de fallback pour ADMIN_TOKEN
    print("Test 2: ADMIN_TOKEN sans fallback")
    print("-" * 40)

    original_token = os.environ.pop("ADMIN_TOKEN", None)

    try:
        result = get_admin_token()
        if result == "dev-token-blade-runner":
            print("✗ VULNERABILITE: Fallback 'dev-token-blade-runner' detecte!")
            vulnerabilities.append("ADMIN_TOKEN a un fallback hardcode")
        elif result is not None and result != "":
            print("✗ VULNERABILITE: Un fallback existe!")
            vulnerabilities.append("ADMIN_TOKEN retourne une valeur sans env var")
        else:
            print("✓ SECURISE: Pas de fallback")
            passed.append("ADMIN_TOKEN")
    except (ValueError, RuntimeError) as e:
        print(f"✓ SECURISE: Leve une erreur sans env var")
        passed.append("ADMIN_TOKEN")
    finally:
        if original_token:
            os.environ["ADMIN_TOKEN"] = original_token
    print()

    # Test 3: Verifier le token frontend
    print("Test 3: Pas de token hardcode dans le frontend")
    print("-" * 40)

    frontend_token = get_frontend_token()
    if frontend_token == 'admin-secure-token-2026':
        print("✗ VULNERABILITE: Token hardcode 'admin-secure-token-2026'!")
        vulnerabilities.append("Frontend a un token hardcode")
    elif frontend_token is not None:
        print("⚠ WARNING: Le frontend retourne un token sans auth")
        warnings.append("Frontend retourne un token sans authentification")
    else:
        print("✓ SECURISE: Pas de token hardcode (retourne None)")
        passed.append("Frontend token")
    print()

    # Test 4: Verifier que verify_admin fonctionne avec un vrai token
    print("Test 4: Authentification avec token valide")
    print("-" * 40)

    os.environ["ADMIN_TOKEN"] = "test-secure-token-12345"
    try:
        creds = HTTPCredentials(credentials="test-secure-token-12345")
        user = verify_admin(creds)
        if user:
            print(f"✓ OK: Authentification reussie pour '{user}'")
            passed.append("Auth avec bon token")
        else:
            print("✗ ERREUR: Authentification devrait retourner un user")
            vulnerabilities.append("verify_admin ne retourne pas de user")
    except HTTPException as e:
        print(f"✗ ERREUR: Token valide rejete: {e.detail}")
        vulnerabilities.append("Token valide rejete")
    except (ValueError, RuntimeError) as e:
        print(f"✓ OK: Validation de config: {e}")
        passed.append("Auth validation")
    finally:
        os.environ.pop("ADMIN_TOKEN", None)
    print()

    # Test 5: Verifier que verify_admin rejette les mauvais tokens
    print("Test 5: Rejet des tokens invalides")
    print("-" * 40)

    os.environ["ADMIN_TOKEN"] = "real-secret-token"
    try:
        creds = HTTPCredentials(credentials="fake-token")
        verify_admin(creds)
        print("✗ VULNERABILITE: Faux token accepte!")
        vulnerabilities.append("Faux token accepte")
    except HTTPException as e:
        if e.status_code == 403:
            print("✓ SECURISE: Faux token rejete correctement")
            passed.append("Rejet faux token")
        else:
            print(f"⚠ WARNING: Code erreur inattendu: {e.status_code}")
            warnings.append(f"Code erreur {e.status_code} au lieu de 403")
    except (ValueError, RuntimeError):
        print("✓ OK: Validation de config avant auth")
        passed.append("Rejet faux token")
    finally:
        os.environ.pop("ADMIN_TOKEN", None)
    print()

    # Resume
    print("="*60)
    print("RESULTAT DE L'AUDIT")
    print("="*60)
    print()

    if vulnerabilities:
        print(f"🔴 VULNERABILITES ({len(vulnerabilities)}):")
        for v in vulnerabilities:
            print(f"   - {v}")
        print()

    if warnings:
        print(f"🟡 WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")
        print()

    if passed:
        print(f"🟢 PASSES ({len(passed)}):")
        for p in passed:
            print(f"   - {p}")
        print()

    print("="*60)
    if vulnerabilities:
        print("❌ AUDIT ECHOUE")
    elif warnings:
        print("⚠️  AUDIT PASSE AVEC WARNINGS")
    else:
        print("✅ AUDIT PASSE - Code securise!")

    print("="*60)


# ============================================================================
# EXPLICATION DE LA CORRECTION
# ============================================================================

def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Les fallbacks dans os.getenv() exposent des secrets dans le code:

    os.getenv("TOKEN", "secret-visible-ici")
                       ^^^^^^^^^^^^^^^^^^^^
                       Visible par tous!

CORRECTIONS:
------------

1. get_admin_password():
   AVANT:  return os.getenv("ADMIN_PASSWORD", "hackathon2026")
   APRES:  password = os.getenv("ADMIN_PASSWORD")
           if not password:
               raise ValueError("ADMIN_PASSWORD required")
           return password

2. get_admin_token():
   AVANT:  return os.getenv("ADMIN_TOKEN", "dev-token-blade-runner")
   APRES:  token = os.getenv("ADMIN_TOKEN")
           if not token:
               raise ValueError("ADMIN_TOKEN required")
           return token

3. get_frontend_token():
   AVANT:  return stored_token or 'admin-secure-token-2026'
   APRES:  return stored_token  # None si pas de token

PRINCIPE:
---------
"Fail fast, fail loud" - L'application doit refuser de
demarrer si elle n'est pas configuree correctement.

Un crash au demarrage est BEAUCOUP mieux qu'une faille
de securite en production!
============================================================
""")


if __name__ == "__main__":
    audit_security()
    print()
    show_explanation()
