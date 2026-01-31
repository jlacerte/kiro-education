"""
Cours 002: Securite - Tokens Hardcodes
======================================
EXERCICE - Code VULNERABLE (version originale)

Niveau: Debutant
Duree: 30-45 minutes

INSTRUCTIONS:
-------------
1. Ce fichier contient des FAILLES DE SECURITE
2. Lance le script pour voir l'audit de securite echouer
3. Corrige les vulnerabilites
4. L'audit doit passer sans warnings

PROBLEMES A TROUVER:
--------------------
- Tokens hardcodes dans le code
- Fallbacks dangereux pour les secrets
- Secrets exposes cote client

Pour lancer l'audit:
    python exercice_original_vulnerable.py
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
# CODE VULNERABLE A CORRIGER
# ============================================================================

def get_admin_password() -> str:
    """
    Recupere le mot de passe admin.

    CORRIGE: Pas de fallback, erreur si variable manquante
    """
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise ValueError("ADMIN_PASSWORD environment variable is required")
    return password


def get_admin_token() -> str:
    """
    Recupere le token admin.

    CORRIGE: Pas de fallback, erreur si variable manquante
    """
    token = os.getenv("ADMIN_TOKEN")
    if not token:
        raise ValueError("ADMIN_TOKEN environment variable is required")
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
    """
    if not token or not token.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    valid_token = get_admin_token()

    if token.credentials != valid_token:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    return "admin_user"


def get_frontend_token() -> str:
    """
    Simule le code JavaScript frontend.

    CORRIGE: Pas de token hardcode, redirection vers login
    """
    stored_token = None  # Simule localStorage.getItem('admin_token')

    # CORRIGE: Pas de fallback, retourne None si pas de token
    if not stored_token:
        # En vrai JS: window.location.href = '/admin/login'
        return None
    
    return stored_token


# ============================================================================
# AUDIT DE SECURITE (ne pas modifier)
# ============================================================================

def audit_security():
    """Execute un audit de securite sur le code."""

    print("="*60)
    print("COURS 002 - Audit de Securite")
    print("="*60)
    print()

    vulnerabilities = []
    warnings = []
    passed = []

    # Test 1: Verifier qu'il n'y a pas de fallback pour ADMIN_PASSWORD
    print("Test 1: ADMIN_PASSWORD sans fallback")
    print("-" * 40)

    # Sauvegarder et supprimer la variable si elle existe
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
        print(f"✓ SECURISE: Leve une erreur sans env var: {e}")
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
        print(f"✓ SECURISE: Leve une erreur sans env var: {e}")
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
        print("✓ SECURISE: Pas de token hardcode")
        passed.append("Frontend token")
    print()

    # Test 4: Verifier que verify_admin fonctionne avec un vrai token
    print("Test 4: Authentification avec token valide")
    print("-" * 40)

    os.environ["ADMIN_TOKEN"] = "test-secure-token-12345"
    try:
        # Devrait fonctionner avec le bon token
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
        # C'est OK si ca leve une erreur de config
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
        print("❌ AUDIT ECHOUE - Corrige les vulnerabilites!")
        print()
        print("INDICES:")
        print("  1. Retire les fallbacks (deuxieme argument de os.getenv)")
        print("  2. Leve une ValueError si la variable n'existe pas")
        print("  3. Le frontend ne doit jamais avoir de token par defaut")
    elif warnings:
        print("⚠️  AUDIT PASSE AVEC WARNINGS")
    else:
        print("✅ AUDIT PASSE - Code securise!")
        print()
        print("FELICITATIONS!")
        print("Tu as elimine toutes les vulnerabilites.")

    print("="*60)


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    audit_security()
