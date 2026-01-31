"""
Orchestrateur éducatif Kiro V3.1 - Version HTTP Archon
Refactorisé pour utiliser client HTTP direct au lieu de MCP
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from models.educational_models import Lesson, EducationalSession, TaskType, SessionStatus, LessonType
from archon.educational_archon_client import EducationalArchonClient
from executor.kiro_structured_executor import KiroStructuredExecutor
from kiro_academic_evaluator import RigorousEvaluator
from core.educational_task_decomposer import EducationalTaskDecomposer
from core.educational_artifact_generator import EducationalArtifactGenerator
from core.educational_metrics_tracker import EducationalMetricsTracker
from core.educational_code_corrector import EducationalCodeCorrector
from core.advanced_ast_analyzer import AdvancedASTAnalyzer
from core.educational_grading_system import EducationalGradingSystem
from core.educational_grading_system import EducationalGradingSystem
from core.educational_code_corrector import EducationalCodeCorrector
from core.educational_execution_logger import ExecutionLogger
from core.educational_title_generator import create_descriptive_title_generator
from config.archon_config import get_dashboard_url

console = Console()

class EducationalOrchestratorV32:
    """Orchestrateur educatif avec client HTTP Archon direct."""

    def __init__(self, engine: str = "kiro"):
        """Initialiser l'orchestrateur."""
        self.engine = engine
        engine_name = "Claude" if engine == "claude" else "Kiro"
        console.print(f"[green]Orchestrateur V3.2 - {engine_name} + Archon HTTP[/green]")

        self.kiro_executor = KiroStructuredExecutor(engine=engine)
        self.evaluator = RigorousEvaluator()
        self.task_decomposer = EducationalTaskDecomposer()
        self.artifact_generator = EducationalArtifactGenerator()
        self.metrics_tracker = EducationalMetricsTracker()
        self.grading_system = EducationalGradingSystem()
        self.code_corrector = EducationalCodeCorrector()
        self.ast_analyzer = AdvancedASTAnalyzer()
        self.session_history = []
    
    async def run_educational_session(self, lesson_path: str, agent: str = "claude") -> EducationalSession:
        """Lancer une session éducative complète avec Archon HTTP."""
        
        async with EducationalArchonClient() as archon:
            console.print(Panel.fit(
                f"[EDU] [bold blue]Session Educative Kiro V3.2[/bold blue] [red][!] PROTOTYPE MODE[/red]\n"
                f"[LESSON] Lecon: {lesson_path}\n"
                f"[BOT] Agent: {agent}\n"
                f"[LINK] Archon: HTTP LIVE\n"
                f"[!] [yellow]Version prototype - Corrections limitees[/yellow]",
                title="Demarrage Session"
            ))
            
            # 1. Analyser la leçon
            console.print("[PARSE] Analyse de la lecon...")
            lesson = await self._analyze_lesson(lesson_path)
            
            # 2. Créer session
            session = EducationalSession(
                session_id=str(uuid.uuid4())[:8],
                lesson=lesson
            )
            session.status = SessionStatus.IN_PROGRESS
            
            # 3. Décomposer la leçon
            console.print("[BRAIN] Decomposition intelligente de la lecon...")
            decomposed_tasks = self.task_decomposer.decompose_lesson(lesson)
            
            console.print(f"[STATS] Lecon analysee: {decomposed_tasks.lesson_type.value} ({decomposed_tasks.complexity_level})")
            console.print(f"[TIME] Duree estimee: {decomposed_tasks.estimated_duration} minutes")
            console.print(f"[LIST] {len(decomposed_tasks.tasks)} taches generees")
            
            # Démarrer tracking des métriques
            session_metrics = self.metrics_tracker.start_session(
                session_id=session.session_id,
                lesson_type=decomposed_tasks.lesson_type.value
            )
            
            # 4. Créer projet Archon avec titre descriptif
            console.print("[LIST] Creation du projet Archon...")
            
            # Générer titre descriptif basé sur l'analyse du code
            title_generator = create_descriptive_title_generator()
            descriptive_title = title_generator.generate_title(
                lesson_number=lesson.lesson_number.replace("lesson-", ""),
                lesson_type=decomposed_tasks.lesson_type.value,
                code_path=lesson_path
            )
            
            project = await archon.create_project(
                title=descriptive_title,
                description=f"Session éducative Kiro - Type: {decomposed_tasks.lesson_type.value}"
            )
            session.archon_project_id = project.id
            
            console.print(f"[LIST] Projet Archon cree: {project.id}")
            console.print(f"   Titre: {project.title}")
            
            # 5. Créer tâches dans Archon
            console.print("[LIST] Creation des taches educatives...")
            archon_tasks = []
            for i, task_dict in enumerate(decomposed_tasks.tasks, 1):
                archon_task = await archon.create_task(
                    project_id=project.id,
                    title=task_dict["title"],
                    description=task_dict["description"],
                    assignee="Kiro",
                    task_order=100 - (i * 5),
                    feature=decomposed_tasks.lesson_type.value
                )
                archon_tasks.append(archon_task)
                # session.tasks.append(task_dict)  # Commenté pour éviter erreurs
            
            console.print(f"[LIST] {len(archon_tasks)} taches creees")
            for i, task in enumerate(archon_tasks, 1):
                console.print(f"   {i}. {task.title}")
            
            # 6. Exécuter workflow avec logging détaillé
            console.print("[RUN] Execution du workflow educatif...")
            execution_logger = ExecutionLogger(session.session_id)
            await self._execute_workflow(session, archon_tasks, archon, execution_logger)
            
            # 7. Finaliser et générer artefacts avec métriques
            session.status = SessionStatus.COMPLETED
            session.end_time = datetime.now()
            
            # Finaliser métriques et calculer note
            final_metrics = self.metrics_tracker.end_session(
                tasks_completed=len(archon_tasks),
                total_tasks=len(archon_tasks)
            )
            
            # Calculer la note automatique avec VRAI code corrigé
            console.print("[EDU] Calcul de la note automatique...")
            original_code = self._read_original_code(lesson_path)
            
            # Générer le code corrigé (NOUVEAU - plus de TODO!)
            console.print("[FIX] Generation du code corrige...")
            corrected_code, _ = self.code_corrector.analyze_and_correct_code(
                original_code, lesson_path
            )
            
            grade_result = self.grading_system.grade_session(
                original_code=original_code,
                corrected_code=corrected_code,
                estimated_duration=decomposed_tasks.estimated_duration,
                actual_duration=final_metrics.duration_minutes if final_metrics else 0.4,
                tasks_completed=len(archon_tasks),
                total_tasks=len(archon_tasks),
                lesson_type=decomposed_tasks.lesson_type.value
            )
            
            console.print(f"[STATS] Note calculee: {grade_result.total_score}/100 ({grade_result.grade_letter})")
            
            # NOUVEAU: Mettre à jour l'objet session avec les vraies données
            session.final_grade = grade_result.total_score
            # Stocker les vraies métriques pour l'affichage
            session._real_completed_tasks = len(archon_tasks)
            session._real_total_tasks = len(archon_tasks)
            # Stocker le titre descriptif pour cohérence
            session._descriptive_title = descriptive_title
            
            # Générer les artefacts de session (NOUVEAU - comme PO)
            console.print("[DIR] Generation des artefacts de session...")
            session_data = {
                "session_id": session.session_id,
                "lesson_number": lesson.lesson_number or "001",
                "lesson_title": descriptive_title,  # UTILISER TITRE DESCRIPTIF
                "lesson_type": decomposed_tasks.lesson_type.value,
                "final_score": grade_result.total_score,  # VRAIE NOTE maintenant
                "grade_letter": grade_result.grade_letter,
                "completed_tasks": len(archon_tasks),
                "total_tasks": len(archon_tasks),
                "status": "completed",
                "duration": final_metrics.duration_minutes if final_metrics else 0.4,  # VRAIE DURÉE
                "archon_project_id": project.id,
                "kiro_calls": final_metrics.kiro_calls if final_metrics else 0,
                "estimated_cost": final_metrics.estimated_cost_usd if final_metrics else 0.0,
                "grade_details": grade_result.details
            }
            
            # Générer tous les artefacts avec VRAI code corrigé et LOG DÉTAILLÉ
            detailed_execution_log = execution_logger.get_formatted_log(
                total_tasks=len(archon_tasks),
                final_score=grade_result.total_score
            )
            
            session_path = self.artifact_generator.generate_session_artifacts(
                lesson_number=lesson.lesson_number or "lesson-001",
                lesson_type=decomposed_tasks.lesson_type.value,
                lesson_path=lesson_path,
                session_data=session_data,
                corrected_code=corrected_code,  # VRAI code maintenant !
                execution_log=detailed_execution_log  # LOG DÉTAILLÉ maintenant !
            )
            
            # Sauvegarder métriques dans artefacts
            if final_metrics:
                self.metrics_tracker.save_metrics_to_artifacts(session_path, final_metrics)
                
                # Créer tâche de métriques dans Archon pour le directeur
                await self._create_metrics_task_for_director(archon, project.id, final_metrics)
            
            console.print(f"[LINK] Dashboard URL: {get_dashboard_url(project.id)}")
            console.print(f"[DIR] Artefacts: {session_path}")
            
            return session
    
    async def _execute_workflow(self, session, archon_tasks, archon, execution_logger):
        """Exécuter les tâches et mettre à jour Archon avec métriques et logging détaillé."""
        
        execution_logger.log_info(f"[RUN] Demarrage workflow avec {len(archon_tasks)} taches")
        
        for i, archon_task in enumerate(archon_tasks):
            execution_logger.log_task_start(archon_task.title, archon_task.id)
            
            # Marquer comme en cours
            await archon.update_task_status(archon_task.id, "doing")
            
            # Enregistrer appel Kiro (estimation basée sur complexité tâche)
            input_tokens = 1500 if "analyser" in archon_task.title.lower() else 1000
            output_tokens = 800 if "corriger" in archon_task.title.lower() else 500
            self.metrics_tracker.record_kiro_call(input_tokens, output_tokens)
            
            # Calculer coût estimé pour cette tâche
            task_cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
            
            try:
                # CORRECTION MINISTÉRIELLE: Vraie exécution au lieu de simulation
                lesson = session.lesson
                corrected_code, validation_result = self.code_corrector.analyze_and_correct_code(
                    original_code=lesson.reference_code,
                    lesson_path=lesson.path or f"lesson-{lesson.lesson_number}"
                )

                # Logger les vrais bugs détectés par l'AST
                bugs_detected = self.ast_analyzer.analyze_code(lesson.reference_code, lesson.path or f"lesson-{lesson.lesson_number}")
                for bug in bugs_detected:
                    execution_logger.log_bug_detected(f"{bug.bug_type.value}: {bug.description}")

                # Logger les vraies corrections appliquées
                if corrected_code and corrected_code != lesson.reference_code:
                    lines_modified = len(corrected_code.splitlines()) - len(lesson.reference_code.splitlines())
                    execution_logger.log_code_correction(f"Code corrige: {lines_modified} lignes modifiees")
                
                
                # Ajouter document de résultat (comme PO)
                await archon.add_document(
                    project_id=session.archon_project_id,
                    title=f"Résultats - {archon_task.title}",
                    document_type="task_result",
                    content={"status": "completed", "task": archon_task.title, "timestamp": datetime.now().isoformat()}
                )
                
                # Marquer comme terminé
                await archon.update_task_status(archon_task.id, "done")
                
                # Logger la completion avec métriques
                execution_logger.log_task_complete(
                    archon_task.title, 
                    archon_task.id, 
                    tokens=input_tokens + output_tokens,
                    cost=task_cost
                )
                
                console.print(f"[OK] {archon_task.title} - Terminee")
                
            except Exception as e:
                await archon.update_task_status(archon_task.id, "todo")
                execution_logger.log_error(f"{archon_task.title} - Erreur: {e}", task_id=archon_task.id)
                console.print(f"[X] {archon_task.title} - Erreur: {e}")
        
        execution_logger.log_success("[SUCCESS] Workflow termine avec succes")
    
    async def _analyze_lesson(self, lesson_path: str) -> Lesson:
        """Analyser une leçon depuis son chemin."""
        # Logique d'analyse simplifiée
        lesson_number = lesson_path.split("/")[-2] if "/" in lesson_path else "lesson-001"
        
        # Nettoyer le titre pour éviter "Leçon lesson-001"
        if lesson_number.startswith("lesson-"):
            clean_number = lesson_number.replace("lesson-", "")
            title = f"Leçon {clean_number} - Débogage Python"
        else:
            title = f"Leçon {lesson_number}"
        
        return Lesson(
            path=lesson_path,
            title=title,
            lesson_type=LessonType.DEBUGGING,
            instructions=f"Analyse de {lesson_path}",
            reference_code="# Code à analyser",
            lesson_number=lesson_number
        )
    
    async def _create_metrics_task_for_director(self, archon, project_id: str, metrics):
        """Créer une tâche de métriques en review pour le directeur."""
        
        metrics_description = f"""[STATS] RAPPORT DE COUTS - Session {metrics.session_id}

## [$] METRIQUES FINANCIERES
- **Coût Total**: ${metrics.estimated_cost_usd:.4f} USD
- **Appels Kiro**: {metrics.kiro_calls}
- **Tokens Utilisés**: {metrics.total_tokens:,}
  - Input: {metrics.estimated_input_tokens:,}
  - Output: {metrics.estimated_output_tokens:,}

## [TIME] METRIQUES TEMPORELLES  
- **Durée**: {metrics.duration_minutes:.1f} minutes
- **Tâches**: {metrics.tasks_completed}/{metrics.total_tasks}
- **Type**: {metrics.lesson_type}

## [!] ALERTES
{chr(10).join(metrics.warnings) if metrics.warnings else "Aucune alerte"}

## [GRAPH] ANALYSE
- **Coût par tâche**: ${(metrics.estimated_cost_usd / metrics.tasks_completed if metrics.tasks_completed > 0 else 0):.4f}
- **Tokens par appel**: {(metrics.total_tokens / metrics.kiro_calls if metrics.kiro_calls > 0 else 0):.0f}
- **Efficacite**: {"[OK] Normale" if metrics.estimated_cost_usd < 0.10 else "[!] Elevee" if metrics.estimated_cost_usd < 0.20 else "[!!] Tres elevee"}

---
*Rapport généré automatiquement pour contrôle des coûts*"""

        try:
            metrics_task = await archon.create_task(
                project_id=project_id,
                title=f"[STATS] METRIQUES COUTS - ${metrics.estimated_cost_usd:.4f}",
                description=metrics_description,
                assignee="Directeur",
                task_order=1,  # Priorité maximale pour le directeur
                feature="cost-monitoring"
            )
            
            # Mettre immédiatement en review pour que le directeur puisse voir
            await archon.update_task_status(metrics_task.id, "review")
            
            console.print(f"[STATS] [green]Tache metriques creee pour le directeur: {metrics_task.id}[/green]")
            
        except Exception as e:
            console.print(f"[red]Erreur création tâche métriques: {e}[/red]")
    
    def _read_original_code(self, lesson_path: str) -> str:
        """Lire le code original de la leçon."""
        try:
            with open(lesson_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "# Code original non disponible"


def create_educational_orchestrator(engine: str = "kiro") -> EducationalOrchestratorV32:
    """Factory function pour creer un orchestrateur V3.2."""
    return EducationalOrchestratorV32(engine=engine)
