"""Educational Grading System.

Automatic grading system for Kiro's educational performance.
Evaluates code quality, functionality, and efficiency.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import ast
import re
from datetime import datetime

@dataclass
class GradingResult:
    """Result of automatic grading."""
    total_score: int  # 0-100
    functionality_score: int  # 0-40
    code_quality_score: int  # 0-30
    efficiency_score: int  # 0-20
    error_detection_score: int  # 0-10
    details: Dict[str, Any]
    grade_letter: str  # A+, A, B+, B, C+, C, D, F

class EducationalGradingSystem:
    """Automatic grading system for educational sessions."""
    
    def __init__(self):
        """Initialize grading system."""
        self.grade_thresholds = {
            95: "A+", 90: "A", 85: "B+", 80: "B", 
            75: "C+", 70: "C", 60: "D", 0: "F"
        }
    
    def grade_session(
        self,
        original_code: str,
        corrected_code: str,
        estimated_duration: int,
        actual_duration: float,
        tasks_completed: int,
        total_tasks: int,
        lesson_type: str = "debugging"
    ) -> GradingResult:
        """Grade a complete educational session.
        
        Args:
            original_code: Original buggy code
            corrected_code: Kiro's corrected code
            estimated_duration: Estimated time in minutes
            actual_duration: Actual time in minutes
            tasks_completed: Number of completed tasks
            total_tasks: Total number of tasks
            lesson_type: Type of lesson
            
        Returns:
            GradingResult with detailed scoring
        """
        
        # 1. Functionality Score (40 points)
        functionality_score = self._grade_functionality(
            original_code, corrected_code, tasks_completed, total_tasks
        )
        
        # 2. Code Quality Score (30 points)
        code_quality_score = self._grade_code_quality(corrected_code)
        
        # 3. Efficiency Score (20 points)
        efficiency_score = self._grade_efficiency(
            estimated_duration, actual_duration
        )
        
        # 4. Error Detection Score (10 points)
        error_detection_score = self._grade_error_detection(
            original_code, corrected_code, lesson_type
        )
        
        # Calculate total
        total_score = (
            functionality_score + 
            code_quality_score + 
            efficiency_score + 
            error_detection_score
        )
        
        # Determine letter grade
        grade_letter = self._get_letter_grade(total_score)
        
        # Detailed breakdown
        details = {
            "functionality": {
                "score": functionality_score,
                "max": 40,
                "criteria": "Code works correctly and completes all tasks"
            },
            "code_quality": {
                "score": code_quality_score,
                "max": 30,
                "criteria": "Clean, readable, well-structured code"
            },
            "efficiency": {
                "score": efficiency_score,
                "max": 20,
                "criteria": "Completed within reasonable time"
            },
            "error_detection": {
                "score": error_detection_score,
                "max": 10,
                "criteria": "Successfully identified and fixed errors"
            },
            "completion_rate": f"{tasks_completed}/{total_tasks}",
            "time_efficiency": f"{actual_duration:.1f}min vs {estimated_duration}min estimated"
        }
        
        return GradingResult(
            total_score=total_score,
            functionality_score=functionality_score,
            code_quality_score=code_quality_score,
            efficiency_score=efficiency_score,
            error_detection_score=error_detection_score,
            details=details,
            grade_letter=grade_letter
        )
    
    def _grade_functionality(self, original_code: str, corrected_code: str, 
                           completed: int, total: int) -> int:
        """Grade functionality (40 points max)."""
        
        # Base score from task completion
        completion_ratio = completed / total if total > 0 else 0
        base_score = int(completion_ratio * 30)  # 30 points for completion
        
        # Bonus points for code improvement
        improvement_score = 0
        
        if corrected_code and corrected_code.strip():
            # Check if corrected code is more than just comments
            if not corrected_code.strip().startswith('#'):
                improvement_score += 5  # Code was actually generated
                
                # Check for Python syntax validity
                try:
                    ast.parse(corrected_code)
                    improvement_score += 5  # Valid Python syntax
                except SyntaxError:
                    pass  # No bonus for invalid syntax
        
        return min(base_score + improvement_score, 40)
    
    def _grade_code_quality(self, corrected_code: str) -> int:
        """Grade code quality (30 points max)."""
        
        # CORRECTION POST-MORTEM: Scoring honnête
        if not corrected_code or corrected_code is None:
            return 0  # Aucune correction = 0 points
        
        # Si c'est juste le code original avec template, 0 points
        if "Code corrigé par Kiro Educational System" in corrected_code:
            return 0  # Template factice détecté
        
        score = 0
        
        if corrected_code and corrected_code.strip():
            # Check for meaningful improvements
            lines = corrected_code.split('\n')
            meaningful_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            
            if len(meaningful_lines) > 10:  # Substantial code
                score += 10
                
                # Check for good practices
                if 'def ' in corrected_code:  # Functions defined
                    score += 5
                if 'class ' in corrected_code:  # Classes defined
                    score += 5
                if '"""' in corrected_code or "'''" in corrected_code:  # Docstrings
                    score += 5
                if 'try:' in corrected_code and 'except' in corrected_code:  # Error handling
                    score += 5
        
        return min(score, 30)
    
    def _grade_efficiency(self, estimated: int, actual: float) -> int:
        """Grade time efficiency (20 points max)."""
        
        if estimated <= 0:
            return 15  # Default good score if no estimation
        
        # Calculate efficiency ratio
        efficiency_ratio = estimated / actual if actual > 0 else 1
        
        if efficiency_ratio >= 10:  # Much faster than expected
            return 20
        elif efficiency_ratio >= 5:  # Significantly faster
            return 18
        elif efficiency_ratio >= 2:  # Faster than expected
            return 16
        elif efficiency_ratio >= 1:  # Met or slightly exceeded expectation
            return 15
        elif efficiency_ratio >= 0.5:  # Took twice as long
            return 10
        else:  # Much slower than expected
            return 5
    
    def _grade_error_detection(self, original_code: str, corrected_code: str, 
                             lesson_type: str) -> int:
        """Grade error detection capability (10 points max)."""
        
        # CORRECTION POST-MORTEM: Scoring honnête pour détection d'erreurs
        if not corrected_code or corrected_code is None:
            return 0  # Aucune correction = 0 points
        
        # Si c'est juste le template factice, 0 points
        if "Code corrigé par Kiro Educational System" in corrected_code:
            return 0  # Template factice détecté
        
        score = 0
        
        # Vérifier si des bugs spécifiques ont été corrigés
        if lesson_type == "debugging":
            # Rechercher des corrections réelles de bugs
            if "where_clause" in original_code and "where_clause" in corrected_code:
                # Vérifier si le bug where_clause a été vraiment corrigé
                if 'where_clause = ""' in corrected_code and 'where_clause = ""' not in original_code:
                    score += 5  # Bug réellement corrigé
            
            if "test-token" in original_code and "admin-token" in corrected_code:
                score += 5  # Token invalide corrigé
        
        # Bonus pour améliorations réelles
        if 'try:' in corrected_code and 'try:' not in original_code:
            score += 2  # Gestion d'erreurs ajoutée
        
        return min(score, 10)
    
    def _get_letter_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        for threshold, grade in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return "F"
    
    def generate_grade_summary(self, result: GradingResult) -> str:
        """Generate human-readable grade summary."""
        
        summary = f"""## [STATS] Évaluation Automatique Kiro

### Score Final: {result.total_score}/100 ({result.grade_letter})

### Détail par Critère:
- **Fonctionnalité**: {result.functionality_score}/40 - {result.details['functionality']['criteria']}
- **Qualité du Code**: {result.code_quality_score}/30 - {result.details['code_quality']['criteria']}
- **Efficacité**: {result.efficiency_score}/20 - {result.details['efficiency']['criteria']}
- **Détection d'Erreurs**: {result.error_detection_score}/10 - {result.details['error_detection']['criteria']}

### Métriques:
- **Tâches Complétées**: {result.details['completion_rate']}
- **Temps d'Exécution**: {result.details['time_efficiency']}

### Interprétation:
{self._get_grade_interpretation(result.total_score)}
"""
        return summary
    
    def _get_grade_interpretation(self, score: int) -> str:
        """Get interpretation of the grade."""
        if score >= 90:
            return "[TROPHY] Excellente performance! Kiro a démontré une maîtrise exceptionnelle."
        elif score >= 80:
            return "✅ Bonne performance! Kiro a bien géré la leçon avec quelques améliorations possibles."
        elif score >= 70:
            return "📈 Performance satisfaisante. Kiro progresse mais peut encore s'améliorer."
        elif score >= 60:
            return "⚠️ Performance acceptable mais des améliorations significatives sont nécessaires."
        else:
            return "🚨 Performance insuffisante. Kiro nécessite des ajustements importants."
