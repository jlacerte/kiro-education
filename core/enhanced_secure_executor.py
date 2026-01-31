"""Enhanced Secure Code Executor - Tests Automatisés Ministériels.

Système d'exécution sécurisée avancé pour valider les corrections
selon le protocole FAIL->PASS du rapport ministériel.
"""

import subprocess
import tempfile
import time
import os
import sys
import sqlite3
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestCase:
    """Cas de test pour validation FAIL->PASS."""
    name: str
    setup_code: str  # Code de setup (DB, fichiers, etc.)
    test_code: str   # Code de test qui doit révéler le bug
    expected_error: str  # Type d'erreur attendue dans l'original
    cleanup_code: str = ""  # Code de nettoyage

@dataclass 
class EnhancedExecutionResult:
    """Résultat d'exécution enrichi avec détails d'erreur."""
    success: bool
    output: str
    error: str
    execution_time: float
    error_type: Optional[str] = None  # NameError, UnboundLocalError, etc.
    line_number: Optional[int] = None
    specific_error: Optional[str] = None

class EnhancedSecureExecutor:
    """Exécuteur sécurisé avancé avec tests spécifiques par leçon."""
    
    def __init__(self):
        """Initialize with lesson-specific test cases."""
        self.test_cases = {
            "lesson-001": TestCase(
                name="Variable non initialisée",
                setup_code='',  # Pas de setup complexe
                test_code='''
# Test direct de la fonction avec conditions vides (révèle le bug UnboundLocalError)
from dataclasses import dataclass

@dataclass
class ContentFilter:
    content_type: str = None
    search_query: str = None
    page: int = 1
    per_page: int = 10

# Simuler la fonction sans dépendances externes
def test_where_clause_bug():
    filters = ContentFilter()  # Aucun filtre
    
    # Reproduire la logique bugguée
    where_conditions = []
    params = []
    
    if filters.content_type:
        where_conditions.append("type = ?")
        params.append(filters.content_type)
    
    if filters.search_query:
        where_conditions.append("content LIKE ?")
        params.append(f"%{filters.search_query}%")
    
    # BUG: where_clause pas initialisé si aucune condition
    if where_conditions:
        where_clause = " WHERE " + " AND ".join(where_conditions)
    
    # ERREUR: where_clause utilisé même si pas initialisé
    query = f"SELECT * FROM content{where_clause} LIMIT {filters.per_page}"
    return query

try:
    result = test_where_clause_bug()
    print(f"SUCCESS: {result}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    raise
''',
                expected_error="UnboundLocalError",
                cleanup_code=""
            ),
            
            "lesson-007": TestCase(
                name="Tests token invalide",
                setup_code='',  # Pas de setup complexe
                test_code='''
# Test direct de la validation JWT (révèle le problème de sécurité)
import jwt

def test_jwt_security():
    # Test avec un token malformé
    malformed_token = "malformed.token.here"
    
    try:
        # Code original avec verify=False (problème de sécurité)
        decoded = jwt.decode(malformed_token, verify=False)
        print(f"Token décodé: {decoded}")
        return True  # Problème: token malformé accepté
    except Exception as e:
        print(f"Token rejeté: {e}")
        return False  # Correct: token malformé rejeté

try:
    result = test_jwt_security()
    print(f"Validation result: {result}")
    # Si verify=False, le token malformé pourrait être accepté (problème)
    # Si verify=True, le token malformé sera rejeté (correct)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    raise
''',
                expected_error="InvalidTokenError",
                cleanup_code=""
            ),
            
            "lesson-008": TestCase(
                name="Routes manquantes",
                setup_code='''
# Setup minimal pour Flask
from flask import Flask
app = Flask(__name__)
''',
                test_code='''
# Test d'accès à route manquante
try:
    with app.test_client() as client:
        response = client.get('/admin/dashboard')
        print(f"Response status: {response.status_code}")
        if response.status_code == 404:
            raise Exception("Route not found")
        print("Route found successfully")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    raise
''',
                expected_error="Exception",
                cleanup_code=""
            )
        }
    
    def execute_with_test_case(self, code: str, lesson_path: str, timeout: int = 15) -> EnhancedExecutionResult:
        """Exécute le code avec un cas de test spécifique à la leçon.
        
        Args:
            code: Code Python à tester
            lesson_path: Chemin de la leçon (ex: "lesson-001")
            timeout: Timeout en secondes
            
        Returns:
            EnhancedExecutionResult avec détails d'erreur
        """
        
        # Identifier la leçon
        lesson_id = self._extract_lesson_id(lesson_path)
        test_case = self.test_cases.get(lesson_id)
        
        if not test_case:
            # Fallback vers exécution simple
            return self._execute_simple(code, timeout)
        
        # Construire le code de test complet
        full_test_code = self._build_test_code(code, test_case)
        
        return self._execute_code_safely(full_test_code, timeout, test_case.expected_error)
    
    def _extract_lesson_id(self, lesson_path: str) -> str:
        """Extrait l'ID de leçon du chemin."""
        if "lesson-001" in lesson_path:
            return "lesson-001"
        elif "lesson-007" in lesson_path:
            return "lesson-007"
        elif "lesson-008" in lesson_path:
            return "lesson-008"
        else:
            return "unknown"
    
    def _build_test_code(self, user_code: str, test_case: TestCase) -> str:
        """Construit le code de test complet."""
        
        # Pour lesson-001, adapter le chemin de DB
        if "lesson-001" in test_case.name:
            # Remplacer "content.db" par le chemin temporaire
            user_code = user_code.replace('"content.db"', 'db_path')
            user_code = user_code.replace("'content.db'", 'db_path')
            # Aussi remplacer les références à "content" par les vraies tables
            user_code = user_code.replace('FROM content', 'FROM (SELECT * FROM videos UNION ALL SELECT video_title as title, created_at FROM transcripts) as content')
            user_code = user_code.replace('SELECT * FROM content', 'SELECT * FROM (SELECT title, created_at FROM videos UNION ALL SELECT video_title as title, created_at FROM transcripts) as content')
        
        full_code = f"""
# === SETUP ===
{test_case.setup_code}

# === USER CODE ===
{user_code}

# === TEST CASE ===
{test_case.test_code}

# === CLEANUP ===
{test_case.cleanup_code}
"""
        return full_code
    
    def _execute_code_safely(self, code: str, timeout: int, expected_error: str) -> EnhancedExecutionResult:
        """Exécute le code de manière sécurisée avec analyse d'erreur."""
        
        try:
            # Créer fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            # Exécuter avec subprocess
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir()
            )
            
            execution_time = time.time() - start_time
            
            # Nettoyer
            os.unlink(temp_file)
            
            # Analyser le résultat
            success = (result.returncode == 0)
            error_type, line_number, specific_error = self._analyze_error(result.stderr)
            
            return EnhancedExecutionResult(
                success=success,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time,
                error_type=error_type,
                line_number=line_number,
                specific_error=specific_error
            )
            
        except subprocess.TimeoutExpired:
            return EnhancedExecutionResult(
                success=False,
                output="",
                error="Timeout: Code execution exceeded time limit",
                execution_time=timeout,
                error_type="TimeoutError"
            )
        except Exception as e:
            return EnhancedExecutionResult(
                success=False,
                output="",
                error=f"Execution error: {str(e)}",
                execution_time=0.0,
                error_type=type(e).__name__
            )
    
    def _execute_simple(self, code: str, timeout: int) -> EnhancedExecutionResult:
        """Exécution simple sans cas de test spécifique."""
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            os.unlink(temp_file)
            
            success = (result.returncode == 0)
            error_type, line_number, specific_error = self._analyze_error(result.stderr)
            
            return EnhancedExecutionResult(
                success=success,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time,
                error_type=error_type,
                line_number=line_number,
                specific_error=specific_error
            )
            
        except Exception as e:
            return EnhancedExecutionResult(
                success=False,
                output="",
                error=f"Error: {str(e)}",
                execution_time=0.0,
                error_type=type(e).__name__
            )
    
    def _analyze_error(self, stderr: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """Analyse les erreurs Python pour extraire type, ligne et détails."""
        
        if not stderr:
            return None, None, None
        
        import re
        
        # Patterns d'erreurs Python courantes
        error_patterns = [
            (r'(\w+Error): (.+)', 'error_type'),
            (r'line (\d+)', 'line_number'),
            (r'UnboundLocalError: (.+)', 'unbound_local'),
            (r'NameError: (.+)', 'name_error'),
            (r'ValueError: (.+)', 'value_error'),
            (r'TypeError: (.+)', 'type_error')
        ]
        
        error_type = None
        line_number = None
        specific_error = None
        
        for pattern, error_kind in error_patterns:
            match = re.search(pattern, stderr)
            if match:
                if error_kind == 'error_type':
                    error_type = match.group(1)
                    specific_error = match.group(2)
                elif error_kind == 'line_number':
                    line_number = int(match.group(1))
                elif error_kind in ['unbound_local', 'name_error', 'value_error', 'type_error']:
                    error_type = error_kind.replace('_', '').title() + 'Error'
                    specific_error = match.group(1)
        
        return error_type, line_number, specific_error
    
    def validate_fail_to_pass(self, original_code: str, corrected_code: str, lesson_path: str) -> bool:
        """Valide le protocole FAIL->PASS selon les standards ministériels.
        
        Returns:
            True si Original FAIL -> Corrigé PASS, False sinon
        """
        
        print(f"[TEST] Validation FAIL->PASS pour {lesson_path}")
        
        # Exécuter le code original
        print("   [DOC] Test code original...")
        original_result = self.execute_with_test_case(original_code, lesson_path)
        
        # Exécuter le code corrigé
        print("   [FIX] Test code corrigé...")
        corrected_result = self.execute_with_test_case(corrected_code, lesson_path)
        
        print(f"   [STATS] Original: {'[OK] PASS' if original_result.success else '[X] FAIL'}")
        print(f"   [STATS] Corrigé:  {'[OK] PASS' if corrected_result.success else '[X] FAIL'}")
        
        if original_result.error_type:
            print(f"   [SEARCH] Erreur originale: {original_result.error_type}")
        
        # Validation selon protocole ministériel
        if original_result.success and corrected_result.success:
            print("   [X] INVALIDE: Les deux codes réussissent - pas de bug détecté")
            return False
        
        if not original_result.success and not corrected_result.success:
            print("   [X] INVALIDE: Les deux codes échouent - correction inefficace")
            return False
        
        if not original_result.success and corrected_result.success:
            print("   [OK] VALIDE: Original FAIL -> Corrigé PASS")
            return True
        
        print("   [X] INVALIDE: Cas improbable - original réussit mais corrigé échoue")
        return False
