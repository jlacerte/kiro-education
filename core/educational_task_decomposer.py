"""
Educational Task Decomposer - Inspiré du Project Orchestrator

Analyse une leçon éducative et génère des tâches adaptées au contexte,
remplaçant les 5 tâches fixes par un système intelligent.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

from models.educational_models import Lesson, LessonType, EducationalTask, TaskType


@dataclass
class DecomposedEducationalTasks:
    """Résultat de la décomposition d'une leçon en tâches"""
    lesson_title: str
    lesson_type: LessonType
    tasks: List[Dict[str, Any]]
    estimated_duration: int  # en minutes
    complexity_level: str  # "beginner", "intermediate", "advanced"


class EducationalTaskDecomposer:
    """Décompose une leçon éducative en tâches adaptées au contexte"""
    
    def __init__(self):
        self.task_templates = self._load_task_templates()
    
    def decompose_lesson(self, lesson: Lesson) -> DecomposedEducationalTasks:
        """Décompose une leçon en tâches adaptées"""
        
        # 1. Analyser le contenu de la leçon
        analysis = self._analyze_lesson_content(lesson)
        
        # 2. Déterminer le type et la complexité
        lesson_type = self._determine_lesson_type(analysis)
        complexity = self._determine_complexity(analysis)
        
        # 3. Générer les tâches adaptées
        tasks = self._generate_adaptive_tasks(lesson_type, complexity, analysis)
        
        # 4. Estimer la durée
        duration = self._estimate_duration(tasks, complexity)
        
        return DecomposedEducationalTasks(
            lesson_title=lesson.title,
            lesson_type=lesson_type,
            tasks=tasks,
            estimated_duration=duration,
            complexity_level=complexity
        )
    
    def _analyze_lesson_content(self, lesson: Lesson) -> Dict[str, Any]:
        """Analyse le contenu de la leçon pour extraire des informations"""
        
        analysis = {
            "has_bug": False,
            "has_security_issue": False,
            "has_tests": False,
            "code_complexity": "simple",
            "keywords": [],
            "file_count": 0,
            "line_count": 0
        }
        
        # Analyser le fichier principal
        if lesson.path and Path(lesson.path).exists():
            content = Path(lesson.path).read_text(encoding='utf-8')
            analysis.update(self._analyze_code_content(content))
            analysis["line_count"] = len(content.splitlines())
            analysis["file_count"] = 1
            
            # Analyser aussi les commentaires/docstrings comme instructions
            analysis.update(self._analyze_instructions(content))
        
        # Analyser les instructions explicites
        if lesson.instructions:
            analysis.update(self._analyze_instructions(lesson.instructions))
        
        return analysis
    
    def _analyze_code_content(self, content: str) -> Dict[str, Any]:
        """Analyse le contenu du code pour détecter des patterns"""
        
        analysis = {}
        content_lower = content.lower()
        
        # Détection de bugs courants
        bug_patterns = [
            r"where_clause\s*=\s*[\"']?\s*[\"']?",  # Variable non initialisée
            r"undefined|not defined",
            r"null|none.*error",
            r"index.*out.*range",
            r"key.*error"
        ]
        
        analysis["has_bug"] = any(re.search(pattern, content_lower) for pattern in bug_patterns)
        
        # Détection de problèmes de sécurité
        security_patterns = [
            r"sql.*injection",
            r"eval\s*\(",
            r"exec\s*\(",
            r"input\s*\(.*\)",  # Input non validé
            r"password.*=.*[\"'][^\"']*[\"']",  # Mot de passe en dur
            r"token.*=.*[\"'][^\"']*[\"']",  # Token en dur
            r"api.*key.*=.*[\"'][^\"']*[\"']",  # API key en dur
            r"secret.*=.*[\"'][^\"']*[\"']",  # Secret en dur
            r"hardcode",  # Hardcodé
            r"vulnerabilit",  # Vulnérabilité
            r"faille.*securit",  # Faille de sécurité
            r"audit.*securit",  # Audit de sécurité
        ]
        
        analysis["has_security_issue"] = any(re.search(pattern, content_lower) for pattern in security_patterns)
        
        # Détection de tests
        test_patterns = [
            r"def test_",
            r"assert ",
            r"unittest",
            r"pytest"
        ]
        
        analysis["has_tests"] = any(re.search(pattern, content_lower) for pattern in test_patterns)
        
        # Complexité du code
        if len(content.splitlines()) > 100:
            analysis["code_complexity"] = "complex"
        elif len(content.splitlines()) > 50:
            analysis["code_complexity"] = "medium"
        else:
            analysis["code_complexity"] = "simple"
        
        # Extraction de mots-clés
        keywords = []
        if "class " in content_lower:
            keywords.append("oop")
        if "def " in content_lower:
            keywords.append("functions")
        if "import " in content_lower:
            keywords.append("modules")
        if "sql" in content_lower:
            keywords.append("database")
        if "web" in content_lower or "http" in content_lower:
            keywords.append("web")
        
        analysis["keywords"] = keywords
        
        return analysis
    
    def _analyze_instructions(self, instructions: str) -> Dict[str, Any]:
        """Analyse les instructions de la leçon"""
        
        analysis = {}
        instructions_lower = instructions.lower()
        
        # Détection des types par mots-clés
        if any(word in instructions_lower for word in ["css", "style", "styling", "textarea", "responsive", "layout", "position", "fixed", "ui", "interface", "multiligne", "multi-ligne"]):
            analysis["instruction_type"] = "css"
        elif any(word in instructions_lower for word in ["test", "testing", "unit", "token", "authentification", "auth", "tdd", "invalide"]):
            analysis["instruction_type"] = "tests"
        elif any(word in instructions_lower for word in ["pattern", "workflow", "detection", "architecture", "design", "avance", "avancé"]):
            analysis["instruction_type"] = "patterns"
        elif any(word in instructions_lower for word in ["clean", "code", "duplication", "mort", "dead", "refactor", "dupliqué", "dupliqu"]):
            analysis["instruction_type"] = "clean_code"
        elif any(word in instructions_lower for word in ["route", "admin", "dashboard", "api", "endpoint", "fixation", "fonctionnelle", "recherche", "multi-sources", "manquant"]):
            analysis["instruction_type"] = "architecture"
        elif any(word in instructions_lower for word in ["debug", "bug", "erreur", "corrig", "silencieux"]):
            analysis["instruction_type"] = "debugging"
        elif any(word in instructions_lower for word in ["sécurité", "security", "vulnérabilité", "faille", "audit", "xss", "injection"]):
            analysis["instruction_type"] = "security"
        else:
            analysis["instruction_type"] = "general"
        
        return analysis
    
    def _determine_lesson_type(self, analysis: Dict[str, Any]) -> LessonType:
        """Détermine le type de leçon basé sur l'analyse"""
        
        # Vérifier d'abord les instructions explicites
        instruction_type = analysis.get("instruction_type", "")
        
        # Patterns CSS
        css_keywords = ["css", "style", "styling", "textarea", "responsive", "layout", "position", "fixed", "ui", "interface"]
        if any(keyword in instruction_type.lower() for keyword in css_keywords):
            return LessonType.CSS
        
        # Patterns Tests
        test_keywords = ["test", "testing", "unit", "token", "authentification", "auth", "tdd"]
        if analysis.get("has_tests") or any(keyword in instruction_type.lower() for keyword in test_keywords):
            return LessonType.TESTS
        
        # Patterns Architecture/Patterns
        pattern_keywords = ["pattern", "workflow", "detection", "architecture", "design"]
        if any(keyword in instruction_type.lower() for keyword in pattern_keywords):
            return LessonType.PATTERNS
        
        # Clean Code
        clean_keywords = ["clean", "code", "duplication", "mort", "dead", "refactor"]
        if any(keyword in instruction_type.lower() for keyword in clean_keywords):
            return LessonType.CLEAN_CODE
        
        # Architecture/Routes
        arch_keywords = ["route", "admin", "dashboard", "api", "endpoint", "fixation", "fonctionnelle", "recherche", "multi-sources"]
        if any(keyword in instruction_type.lower() for keyword in arch_keywords):
            return LessonType.ARCHITECTURE
        
        # Types existants
        if analysis.get("has_bug") or "debug" in instruction_type.lower():
            return LessonType.DEBUGGING
        elif analysis.get("has_security_issue") or "security" in instruction_type.lower():
            return LessonType.SECURITY
        else:
            return LessonType.EXERCISE
    
    def _determine_complexity(self, analysis: Dict[str, Any]) -> str:
        """Détermine la complexité de la leçon"""
        
        complexity_score = 0
        
        # Facteurs de complexité
        if analysis.get("code_complexity") == "complex":
            complexity_score += 3
        elif analysis.get("code_complexity") == "medium":
            complexity_score += 2
        else:
            complexity_score += 1
        
        if analysis.get("line_count", 0) > 100:
            complexity_score += 2
        elif analysis.get("line_count", 0) > 50:
            complexity_score += 1
        
        if len(analysis.get("keywords", [])) > 3:
            complexity_score += 1
        
        # Classification
        if complexity_score >= 5:
            return "advanced"
        elif complexity_score >= 3:
            return "intermediate"
        else:
            return "beginner"
    
    def _generate_adaptive_tasks(self, lesson_type: LessonType, complexity: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des tâches adaptées au type de leçon et à la complexité"""
        
        tasks = []
        
        # Tâche d'analyse (toujours présente)
        tasks.append({
            "type": TaskType.ANALYZE,
            "title": f"Analyser la leçon {lesson_type.value}",
            "description": f"Analyser le code et identifier les {self._get_focus_area(lesson_type)}",
            "estimated_minutes": 3 if complexity == "beginner" else 5
        })
        
        # Tâches spécifiques au type
        if lesson_type == LessonType.DEBUGGING:
            tasks.extend(self._generate_debugging_tasks(complexity, analysis))
        elif lesson_type == LessonType.SECURITY:
            tasks.extend(self._generate_security_tasks(complexity, analysis))
        else:  # EXERCISE (inclut les tests)
            tasks.extend(self._generate_exercise_tasks(complexity, analysis))
        
        # Tâches de finalisation
        tasks.extend(self._generate_finalization_tasks(complexity))
        
        return tasks
    
    def _generate_debugging_tasks(self, complexity: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des tâches spécifiques au debugging"""
        
        tasks = []
        
        # Identification du bug
        tasks.append({
            "type": TaskType.EXECUTE,
            "title": "Identifier le bug principal",
            "description": "Localiser et comprendre la cause du dysfonctionnement",
            "estimated_minutes": 5 if complexity == "beginner" else 10
        })
        
        # Correction
        tasks.append({
            "type": TaskType.EXECUTE,
            "title": "Corriger le bug identifié",
            "description": "Appliquer la correction minimale et appropriée",
            "estimated_minutes": 3 if complexity == "beginner" else 8
        })
        
        # Validation si complexe
        if complexity in ["intermediate", "advanced"]:
            tasks.append({
                "type": TaskType.EXECUTE,
                "title": "Valider la correction avec tests",
                "description": "Vérifier que la correction fonctionne et n'introduit pas de régression",
                "estimated_minutes": 5
            })
        
        return tasks
    
    def _generate_security_tasks(self, complexity: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des tâches spécifiques à la sécurité"""
        
        tasks = []
        
        tasks.append({
            "type": TaskType.EXECUTE,
            "title": "Identifier les vulnérabilités",
            "description": "Détecter les failles de sécurité dans le code",
            "estimated_minutes": 8 if complexity == "beginner" else 15
        })
        
        tasks.append({
            "type": TaskType.EXECUTE,
            "title": "Implémenter les corrections sécurisées",
            "description": "Appliquer les bonnes pratiques de sécurité",
            "estimated_minutes": 10 if complexity == "beginner" else 20
        })
        
        return tasks
    
    def _generate_exercise_tasks(self, complexity: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des tâches pour un exercice général (inclut les tests)"""
        
        tasks = []
        
        # Si c'est orienté tests
        if analysis.get("has_tests") or analysis.get("instruction_type") == "testing":
            tasks.append({
                "type": TaskType.EXECUTE,
                "title": "Créer les tests unitaires",
                "description": "Développer une suite de tests complète",
                "estimated_minutes": 15 if complexity == "beginner" else 25
            })
            
            tasks.append({
                "type": TaskType.EXECUTE,
                "title": "Valider la couverture de tests",
                "description": "Vérifier que tous les cas sont couverts",
                "estimated_minutes": 5 if complexity == "beginner" else 10
            })
        else:
            # Exercice général
            tasks.append({
                "type": TaskType.EXECUTE,
                "title": "Implémenter la solution",
                "description": "Développer la solution selon les spécifications",
                "estimated_minutes": 10 if complexity == "beginner" else 20
            })
            
            if complexity in ["intermediate", "advanced"]:
                tasks.append({
                    "type": TaskType.EXECUTE,
                    "title": "Optimiser et documenter",
                    "description": "Améliorer la solution et ajouter la documentation",
                    "estimated_minutes": 8
                })
        
        return tasks
    
    def _generate_finalization_tasks(self, complexity: str) -> List[Dict[str, Any]]:
        """Génère les tâches de finalisation"""
        
        tasks = []
        
        # Évaluation
        tasks.append({
            "type": TaskType.EVALUATE,
            "title": "Évaluer la performance de Kiro",
            "description": "Analyser la qualité de la solution et attribuer une note",
            "estimated_minutes": 3
        })
        
        # Archivage
        tasks.append({
            "type": TaskType.ARCHIVE,
            "title": "Archiver la solution et les artefacts",
            "description": "Sauvegarder tous les fichiers et résultats",
            "estimated_minutes": 2
        })
        
        # Rapport
        tasks.append({
            "type": TaskType.REPORT,
            "title": "Générer le rapport final",
            "description": "Créer le bulletin académique et la documentation",
            "estimated_minutes": 3
        })
        
        return tasks
    
    def _get_focus_area(self, lesson_type: LessonType) -> str:
        """Retourne la zone de focus selon le type de leçon"""
        
        focus_areas = {
            LessonType.DEBUGGING: "bugs et dysfonctionnements",
            LessonType.SECURITY: "vulnérabilités de sécurité",
            LessonType.EXERCISE: "exigences et spécifications"
        }
        
        return focus_areas.get(lesson_type, "éléments clés")
    
    def _estimate_duration(self, tasks: List[Dict[str, Any]], complexity: str) -> int:
        """Estime la durée totale en minutes"""
        
        base_duration = sum(task.get("estimated_minutes", 5) for task in tasks)
        
        # Facteur de complexité
        complexity_factors = {
            "beginner": 1.0,
            "intermediate": 1.3,
            "advanced": 1.6
        }
        
        return int(base_duration * complexity_factors.get(complexity, 1.0))
    
    def _load_task_templates(self) -> Dict[str, Any]:
        """Charge les templates de tâches (pour extension future)"""
        
        # Pour l'instant, templates intégrés
        # Dans le futur, on pourrait charger depuis des fichiers JSON/YAML
        return {
            "debugging": {
                "focus": "Identification et correction de bugs",
                "skills": ["debugging", "problem_solving", "testing"]
            },
            "security": {
                "focus": "Sécurisation du code",
                "skills": ["security", "best_practices", "validation"]
            },
            "testing": {
                "focus": "Création de tests robustes",
                "skills": ["testing", "quality_assurance", "coverage"]
            },
            "exercise": {
                "focus": "Implémentation selon spécifications",
                "skills": ["programming", "design", "documentation"]
            }
        }
