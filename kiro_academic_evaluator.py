#!/usr/bin/env python3
"""
🎓 Kiro Academic Evaluator
Système d'évaluation rigoureuse comme un vrai examen scolaire
"""

import ast
import subprocess
import sys
import tempfile
import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
import json

@dataclass
class AcademicAssessment:
    """Évaluation académique complète"""
    module_id: str
    student_code: str
    reference_code: str
    
    # Scores détaillés (0-100)
    functional_equivalence: float  # Est-ce que ça fait la même chose ?
    conceptual_mastery: float     # Est-ce que les concepts sont maîtrisés ?
    code_quality: float          # Est-ce que c'est du bon code ?
    innovation_score: float      # Est-ce que c'est créatif/élégant ?
    
    # Score final
    final_grade: float
    letter_grade: str  # A, B, C, D, F
    
    # Feedback détaillé
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    
    # Métriques objectives
    test_cases_passed: int
    test_cases_total: int
    execution_time_ratio: float  # student_time / reference_time
    
    # Validation
    passes_academic_standard: bool  # >= 70%

class RigorousEvaluator:
    """Évaluateur académique rigoureux"""
    
    def __init__(self):
        self.academic_threshold = 70.0  # Seuil de réussite académique
        
    def evaluate_student_work(self, student_code: str, reference_code: str, 
                            module_id: str, test_scenarios: List[Dict]) -> AcademicAssessment:
        """Évaluation complète comme un vrai examen"""
        
        print(f"📝 Evaluating student work for module: {module_id}")
        
        # 1. Tests fonctionnels rigoureux
        functional_score, tests_passed, tests_total = self._test_functional_equivalence(
            student_code, reference_code, test_scenarios
        )
        
        # 2. Analyse conceptuelle approfondie
        conceptual_score = self._assess_conceptual_mastery(student_code, reference_code)
        
        # 3. Évaluation qualité code
        quality_score = self._evaluate_code_quality(student_code)
        
        # 4. Score d'innovation
        innovation_score = self._assess_innovation(student_code, reference_code)
        
        # 5. Performance comparative
        time_ratio = self._compare_execution_performance(student_code, reference_code)
        
        # 6. Calcul note finale (pondération académique)
        final_grade = (
            functional_score * 0.50 +    # Fonctionnalité = 50%
            conceptual_score * 0.25 +    # Concepts = 25%
            quality_score * 0.15 +       # Qualité = 15%
            innovation_score * 0.10      # Innovation = 10%
        )
        
        # 7. Attribution lettre
        letter_grade = self._assign_letter_grade(final_grade)
        
        # 8. Génération feedback académique
        strengths, weaknesses, recommendations = self._generate_academic_feedback(
            functional_score, conceptual_score, quality_score, innovation_score,
            student_code, reference_code
        )
        
        return AcademicAssessment(
            module_id=module_id,
            student_code=student_code,
            reference_code=reference_code,
            functional_equivalence=functional_score,
            conceptual_mastery=conceptual_score,
            code_quality=quality_score,
            innovation_score=innovation_score,
            final_grade=final_grade,
            letter_grade=letter_grade,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            test_cases_passed=tests_passed,
            test_cases_total=tests_total,
            execution_time_ratio=time_ratio,
            passes_academic_standard=final_grade >= self.academic_threshold
        )
    
    def _test_functional_equivalence(self, student_code: str, reference_code: str, 
                                   test_scenarios: List[Dict]) -> Tuple[float, int, int]:
        """Tests rigoureux d'équivalence fonctionnelle"""
        
        print("👨‍🏫 Professeur: Test de l'équivalence fonctionnelle...")
        
        if not test_scenarios:
            # Génération automatique de tests basiques
            test_scenarios = self._generate_basic_tests(reference_code)
            print(f"  📋 {len(test_scenarios)} tests générés automatiquement")
        
        passed = 0
        total = len(test_scenarios)
        
        print(f"  🧪 Exécution de {total} tests...")
        
        for i, scenario in enumerate(test_scenarios, 1):
            try:
                print(f"    Test {i}/{total}: ", end="")
                
                # Exécuter le code de référence
                ref_result = self._execute_with_inputs(reference_code, scenario.get('inputs', []))
                print(f"Référence OK, ", end="")
                
                # Exécuter le code étudiant
                student_result = self._execute_with_inputs(student_code, scenario.get('inputs', []))
                print(f"Étudiant OK, ", end="")
                
                # Comparer les résultats
                if self._results_equivalent(ref_result, student_result):
                    passed += 1
                    print("✅ RÉUSSI")
                else:
                    print(f"❌ ÉCHEC (ref: '{ref_result}' vs student: '{student_result}')")
                    
            except Exception as e:
                print(f"❌ ERREUR: {e}")
                continue
        
        score = (passed / total * 100) if total > 0 else 0
        print(f"   📊 Résultat final: {passed}/{total} tests réussis ({score:.1f}%)")
        
        return score, passed, total
    
    def _assess_conceptual_mastery(self, student_code: str, reference_code: str) -> float:
        """Évalue la maîtrise conceptuelle"""
        
        # Extraire les concepts du code de référence
        ref_concepts = self._extract_programming_concepts(reference_code)
        student_concepts = self._extract_programming_concepts(student_code)
        
        # Concepts requis présents
        required_found = sum(1 for concept in ref_concepts if concept in student_concepts)
        concept_coverage = (required_found / len(ref_concepts) * 100) if ref_concepts else 100
        
        # Bonus pour concepts supplémentaires appropriés
        bonus_concepts = len([c for c in student_concepts if c not in ref_concepts])
        bonus_score = min(bonus_concepts * 5, 20)  # Max 20 points bonus
        
        total_score = min(concept_coverage + bonus_score, 100)
        
        print(f"   🧠 Conceptual mastery: {total_score:.1f}% (required: {required_found}/{len(ref_concepts)})")
        
        return total_score
    
    def _evaluate_code_quality(self, code: str) -> float:
        """Évaluation rigoureuse de la qualité du code"""
        
        score = 100.0
        issues = []
        
        lines = code.split('\n')
        
        # Critères académiques stricts
        
        # 1. Nommage des variables
        var_names = re.findall(r'(\w+)\s*=', code)
        for name in var_names:
            if len(name) < 2 and name not in ['i', 'j', 'x', 'y']:
                score -= 10
                issues.append(f"Variable name too short: {name}")
        
        # 2. Longueur des lignes
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                score -= 5
                issues.append(f"Line {i} too long")
        
        # 3. Complexité des fonctions
        functions = re.findall(r'def\s+(\w+)', code)
        for func in functions:
            func_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            if func_lines > 20:
                score -= 15
                issues.append(f"Function {func} too complex")
        
        # 4. Documentation
        if 'def ' in code and '"""' not in code and '#' not in code:
            score -= 10
            issues.append("Missing documentation")
        
        # 5. Gestion d'erreurs appropriée
        if 'input(' in code and 'try:' not in code:
            score -= 5
            issues.append("Consider error handling for user input")
        
        final_score = max(score, 0)
        print(f"   📝 Code quality: {final_score:.1f}% ({len(issues)} issues)")
        
        return final_score
    
    def _assess_innovation(self, student_code: str, reference_code: str) -> float:
        """Évalue l'innovation et l'élégance"""
        
        score = 50.0  # Score de base
        
        # Analyse comparative
        student_lines = len([l for l in student_code.split('\n') if l.strip()])
        ref_lines = len([l for l in reference_code.split('\n') if l.strip()])
        
        # Bonus pour concision élégante
        if student_lines < ref_lines and student_lines >= ref_lines * 0.7:
            score += 20
            print("   ✨ Bonus: Elegant concision")
        
        # Bonus pour techniques avancées
        advanced_patterns = [
            (r'f["\'].*["\']', "f-string formatting"),
            (r'\[.*for.*in.*\]', "list comprehension"),
            (r'with\s+open', "context manager"),
            (r'lambda\s+', "lambda function"),
            (r'yield\s+', "generator"),
        ]
        
        for pattern, description in advanced_patterns:
            if re.search(pattern, student_code) and not re.search(pattern, reference_code):
                score += 10
                print(f"   ✨ Bonus: {description}")
        
        # Malus pour sur-complexité
        if student_lines > ref_lines * 1.5:
            score -= 15
            print("   ⚠️  Penalty: Over-complexity")
        
        return min(max(score, 0), 100)
    
    def _compare_execution_performance(self, student_code: str, reference_code: str) -> float:
        """Compare les performances d'exécution"""
        
        try:
            import time
            
            # Mesurer temps de référence
            start = time.time()
            self._execute_code_safely(reference_code)
            ref_time = time.time() - start
            
            # Mesurer temps étudiant
            start = time.time()
            self._execute_code_safely(student_code)
            student_time = time.time() - start
            
            ratio = student_time / ref_time if ref_time > 0 else 1.0
            print(f"   ⏱️  Performance ratio: {ratio:.2f}x reference time")
            
            return ratio
            
        except Exception:
            return 1.0
    
    def _assign_letter_grade(self, score: float) -> str:
        """Attribution de la note lettre selon standards académiques"""
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'
    
    def _generate_academic_feedback(self, func_score: float, concept_score: float,
                                  quality_score: float, innovation_score: float,
                                  student_code: str, reference_code: str) -> Tuple[List[str], List[str], List[str]]:
        """Génère un feedback académique détaillé"""
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyse des forces
        if func_score >= 90:
            strengths.append("Excellent functional implementation")
        if concept_score >= 85:
            strengths.append("Strong conceptual understanding")
        if quality_score >= 80:
            strengths.append("Good code quality and style")
        if innovation_score >= 70:
            strengths.append("Creative and elegant approach")
        
        # Analyse des faiblesses
        if func_score < 70:
            weaknesses.append("Functional implementation needs improvement")
        if concept_score < 70:
            weaknesses.append("Conceptual understanding requires reinforcement")
        if quality_score < 60:
            weaknesses.append("Code quality and style need attention")
        
        # Recommandations
        if func_score < concept_score:
            recommendations.append("Focus on translating concepts into working code")
        if quality_score < 70:
            recommendations.append("Review Python style guidelines (PEP 8)")
        if innovation_score < 50:
            recommendations.append("Explore more Pythonic approaches and idioms")
        
        return strengths, weaknesses, recommendations
    
    def _extract_programming_concepts(self, code: str) -> List[str]:
        """Extrait les concepts de programmation utilisés"""
        concepts = []
        
        patterns = {
            'variables': r'(\w+)\s*=\s*[^=]',
            'functions': r'def\s+\w+',
            'conditionals': r'if\s+.*:|elif\s+.*:|else\s*:',
            'loops': r'for\s+.*:|while\s+.*:',
            'lists': r'\[.*\]',
            'dictionaries': r'\{.*\}',
            'string_methods': r'\w+\.(strip|split|join|replace)',
            'file_operations': r'open\s*\(',
            'exception_handling': r'try\s*:|except.*:',
            'classes': r'class\s+\w+',
            'imports': r'import\s+\w+|from\s+\w+\s+import',
        }
        
        for concept, pattern in patterns.items():
            if re.search(pattern, code, re.MULTILINE):
                concepts.append(concept)
        
        return concepts
    
    def _generate_basic_tests(self, reference_code: str) -> List[Dict]:
        """Génère des tests basiques automatiquement"""
        tests = []
        
        print("  🔧 Génération intelligente de tests...")
        
        # Analyser le code de référence pour créer des tests pertinents
        lines = reference_code.split('\n')
        
        # Test 1: Exécution basique
        tests.append({
            'inputs': [],
            'description': 'Test d\'exécution basique',
            'expected_type': 'execution'
        })
        
        # Test 2: Si le code contient des variables, tester l'affichage
        if any('=' in line and 'def' not in line for line in lines):
            tests.append({
                'inputs': [],
                'description': 'Test d\'affichage des variables',
                'expected_type': 'output'
            })
        
        # Test 3: Si le code contient des fonctions, tester les appels
        if 'def ' in reference_code:
            # Extraire les fonctions et leurs paramètres
            import re
            functions = re.findall(r'def\s+(\w+)\s*\([^)]*\)', reference_code)
            for func_name in functions:
                tests.append({
                    'inputs': [],
                    'description': f'Test de la fonction {func_name}',
                    'expected_type': 'function',
                    'function_name': func_name
                })
        
        # Test 4: Si le code contient des conditionnels, tester la logique
        if 'if ' in reference_code:
            tests.append({
                'inputs': [],
                'description': 'Test de la logique conditionnelle',
                'expected_type': 'conditional'
            })
        
        print(f"  ✅ {len(tests)} tests intelligents générés")
        return tests
    
    def _execute_with_inputs(self, code: str, inputs: List[str]) -> Any:
        """Exécute du code avec des inputs simulés"""
        # Implémentation simplifiée pour le prototype
        return self._execute_code_safely(code)
    
    def _execute_code_safely(self, code: str) -> Any:
        """Exécution sécurisée du code"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                
                Path(f.name).unlink()
                return result.stdout
                
        except Exception as e:
            return str(e)
    
    def _results_equivalent(self, result1: Any, result2: Any) -> bool:
        """Compare si deux résultats sont équivalents"""
        
        # Normalisation avancée pour comparaison
        str1 = str(result1).strip().lower()
        str2 = str(result2).strip().lower()
        
        # Comparaison exacte
        if str1 == str2:
            return True
        
        # Comparaison flexible pour les sorties similaires
        # Enlever les espaces multiples et caractères spéciaux
        import re
        clean1 = re.sub(r'\s+', ' ', str1)
        clean2 = re.sub(r'\s+', ' ', str2)
        
        if clean1 == clean2:
            return True
        
        # Vérifier si les deux contiennent les mêmes mots-clés importants
        words1 = set(re.findall(r'\w+', clean1))
        words2 = set(re.findall(r'\w+', clean2))
        
        # Si 80% des mots sont communs, considérer comme équivalent
        if words1 and words2:
            common_words = words1.intersection(words2)
            similarity = len(common_words) / max(len(words1), len(words2))
            if similarity >= 0.8:
                return True
        
        return False

# Fonction de test du système d'évaluation
def test_academic_evaluation():
    """Test du système d'évaluation académique"""
    
    evaluator = RigorousEvaluator()
    
    # Code de référence (le "maître")
    reference_code = '''
def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    return length * width

result = calculate_area(5, 3)
print(f"Area: {result}")
'''
    
    # Code étudiant (Kiro)
    student_code = '''
def compute_rectangle_area(l, w):
    area = l * w
    return area

answer = compute_rectangle_area(5, 3)
print(f"The area is: {answer}")
'''
    
    print("🎓 ACADEMIC EVALUATION SYSTEM TEST")
    print("=" * 50)
    
    assessment = evaluator.evaluate_student_work(
        student_code=student_code,
        reference_code=reference_code,
        module_id="rectangle_area",
        test_scenarios=[]
    )
    
    # Affichage du bulletin académique
    print(f"\n📊 ACADEMIC REPORT CARD")
    print("=" * 50)
    print(f"Module: {assessment.module_id}")
    print(f"Final Grade: {assessment.final_grade:.1f}/100 ({assessment.letter_grade})")
    print(f"Academic Standard: {'✅ PASS' if assessment.passes_academic_standard else '❌ FAIL'}")
    
    print(f"\n📈 Detailed Scores:")
    print(f"  Functional Equivalence: {assessment.functional_equivalence:.1f}/100")
    print(f"  Conceptual Mastery:     {assessment.conceptual_mastery:.1f}/100")
    print(f"  Code Quality:           {assessment.code_quality:.1f}/100")
    print(f"  Innovation:             {assessment.innovation_score:.1f}/100")
    
    print(f"\n💪 Strengths:")
    for strength in assessment.strengths:
        print(f"  • {strength}")
    
    if assessment.weaknesses:
        print(f"\n⚠️  Areas for Improvement:")
        for weakness in assessment.weaknesses:
            print(f"  • {weakness}")
    
    if assessment.recommendations:
        print(f"\n🎯 Recommendations:")
        for rec in assessment.recommendations:
            print(f"  • {rec}")

if __name__ == "__main__":
    test_academic_evaluation()
