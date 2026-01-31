"""
Cours 002: Securite - Tokens Hardcodes
======================================
SOLUTION CORRIGEE

Cette solution élimine toutes les vulnérabilités de sécurité :
1. ✅ Pas de fallback pour ADMIN_PASSWORD
2. ✅ Pas de fallback pour ADMIN_TOKEN  
3. ✅ Pas de token hardcodé dans le frontend
4. ✅ Erreurs explicites si variables manquantes
5. ✅ Authentification sécurisée
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass


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
# CODE SECURISE - SOLUTION
# ============================================================================

def get_admin_password() -> str:
    """
    Recupere le mot de passe admin depuis les variables d'environnement.
    SECURISE: Pas de fallback, erreur explicite si manquant.
    """
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
    SECURISE: Pas de fallback, erreur explicite si manquant.
    """
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
    SECURISE: Utilise les tokens configurés par environnement.
    """
    if not token or not token.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Récupérer le token valide (lève une erreur si non configuré)
    valid_token = get_admin_token()

    if token.credentials != valid_token:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    return "admin_user"


def get_frontend_token() -> Optional[str]:
    """
    Simule le code JavaScript frontend.
    SECURISE: Pas de token hardcodé, redirection vers login si nécessaire.
    """
    stored_token = None  # Simule localStorage.getItem('admin_token')

    if not stored_token:
        # En vrai JavaScript: window.location.href = '/admin/login'
        # Ici on retourne None pour indiquer qu'il faut s'authentifier
        return None
    
    return stored_token


def validate_environment():
    """
    Valide que toutes les variables d'environnement requises sont présentes.
    SECURISE: Fail fast, fail loud - refuse de démarrer si mal configuré.
    """
    required_vars = ["ADMIN_TOKEN", "ADMIN_PASSWORD"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {missing}. "
            f"Set them before starting the application."
        )


# ============================================================================
# EXEMPLE D'UTILISATION SECURISEE
# ============================================================================

def main():
    """Exemple d'utilisation sécurisée"""
    try:
        # Valider la configuration au démarrage
        validate_environment()
        print("✅ Configuration validée")
        
        # Simuler une authentification
        test_token = HTTPCredentials(credentials=get_admin_token())
        user = verify_admin(test_token)
        print(f"✅ Authentification réussie pour: {user}")
        
    except ValueError as e:
        print(f"❌ Erreur de configuration: {e}")
        return 1
    except HTTPException as e:
        print(f"❌ Erreur d'authentification: {e.detail}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
