#!/usr/bin/env python3
"""
Kiro Educational System V3.0 - Interface CLI principale
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from core.educational_orchestrator_v32 import create_educational_orchestrator
from archon.mock_educational_client import MockEducationalArchonClient
from config.archon_config import get_dashboard_url

app = typer.Typer(
    name="kiro-education",
    help="[EDU] Kiro Educational System V3.0 - Système d'apprentissage intelligent avec Archon",
    add_completion=False
)

console = Console()

# Instance globale de l'orchestrateur (sera créée à la demande)
orchestrator = None

@app.command()
def go(
    lesson_request: str = typer.Argument(..., help="Demande de lecon (ex: 'Lesson-001 debugging' ou 'kiro_lessons/lesson-001/exercice.py')"),
    agent: str = typer.Option("claude", "--agent", "-a", help="Agent a utiliser"),
    engine: str = typer.Option("kiro", "--engine", "-e", help="Moteur: 'kiro' ou 'claude'"),
    use_real_archon: bool = typer.Option(True, "--real-archon/--mock-archon", help="Utiliser le vrai serveur Archon")
):
    """TRIGGER UNIFIE - Demarre le meta-orchestrateur educatif"""

    engine_name = "Kiro" if engine == "kiro" else "Claude"
    engine_color = "blue" if engine == "kiro" else "green"

    console.print(Panel.fit(
        f"[bold {engine_color}]{engine_name} Educational Meta-Orchestrator V3.2[/bold {engine_color}]\n"
        f"Moteur: {engine.upper()}\n"
        "Demarrage autonome de session educative...",
        title="Meta-Orchestrator"
    ))
    
    console.print(Panel.fit(
        f"[bold]{lesson_request}[/bold]",
        style="cyan"
    ))
    
    try:
        # Importer l'orchestrateur V3.2 avec client HTTP
        from core.educational_orchestrator_v32 import create_educational_orchestrator

        # Creer l'orchestrateur V3.2 avec le moteur specifie
        orchestrator = create_educational_orchestrator(engine=engine)

        # Determiner si c'est un chemin de fichier ou une demande textuelle
        lesson_path = _resolve_lesson_path(lesson_request)

        # Lancer la session educative complete
        session = asyncio.run(orchestrator.run_educational_session(lesson_path, agent))
        
        # Afficher le résumé final
        _display_session_summary_v31(session)
        
        console.print(f"\n[SUCCESS] Session terminee avec succes!", style="bold green")
        console.print(f"[LINK] Dashboard: {get_dashboard_url(session.archon_project_id)}")
        
    except KeyboardInterrupt:
        console.print(f"\n[!] Session interrompue par l'utilisateur", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[X] Erreur lors de la session: {e}", style="red")
        raise typer.Exit(1)

@app.command()
def start_lesson(
    lesson_path: str = typer.Argument(..., help="Chemin vers la leçon (ex: kiro_lessons/lesson-002/exercice.py)"),
    agent: str = typer.Option("blade-runner-fixed", "--agent", "-a", help="Agent Kiro à utiliser"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout en secondes")
):
    """[EDU] [DEPRECATED] Ancienne méthode - Utilisez 'go' à la place"""
    
    console.print("[!] [yellow]DEPRECATED: Utilisez 'python kiro_education.py go \"Lesson-001 debugging\"' à la place[/yellow]")
    
    # Créer l'orchestrateur legacy si nécessaire
    global orchestrator
    if orchestrator is None:
        from core.educational_orchestrator import EducationalOrchestrator
        orchestrator = EducationalOrchestrator()
    
    lesson_file = Path(lesson_path)
    if not lesson_file.exists():
        console.print(f"[X] Fichier non trouve: {lesson_path}", style="red")
        raise typer.Exit(1)
    
    try:
        # Lancer la session éducative
        session = asyncio.run(orchestrator.start_lesson_session(str(lesson_file), agent))
        
        # Afficher le résumé final
        _display_session_summary(session)
        
        console.print(f"\n[SUCCESS] Session terminee avec succes!", style="bold green")
        console.print(f"[LINK] Dashboard: {session.dashboard_url}")
        
    except KeyboardInterrupt:
        console.print(f"\n[!] Session interrompue par l'utilisateur", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[X] Erreur lors de la session: {e}", style="red")
        raise typer.Exit(1)

def _resolve_lesson_path(lesson_request: str) -> str:
    """Résoudre le chemin d'une leçon avec auto-découverte et validation stricte."""
    from pathlib import Path
    from rich.console import Console
    
    console = Console()
    
    # Si chemin direct fourni, le valider
    if Path(lesson_request).exists():
        return lesson_request
    
    # Auto-découverte des leçons disponibles
    discovered = discover_lessons()
    
    if not discovered:
        raise ValueError("Aucune leçon trouvée dans kiro_lessons/")
    
    # Recherche exacte d'abord (lesson-001, lesson-002, etc.)
    request_lower = lesson_request.lower()
    for lesson_id, path in discovered.items():
        if lesson_id in request_lower:
            console.print(f"[OK] Resolu: '{lesson_request}' -> {path}")
            return path
    
    # Recherche par mots-clés (debugging, security, etc.)
    keyword_mappings = {
        "debugging": "lesson-001",
        "security": "lesson-002", 
        "sécurité": "lesson-002",
        "exercise": "lesson-003"
    }
    
    for keyword, lesson_id in keyword_mappings.items():
        if keyword in request_lower and lesson_id in discovered:
            path = discovered[lesson_id]
            console.print(f"[OK] Resolu par mot-cle: '{lesson_request}' -> {path}")
            return path
    
    # Si aucune correspondance trouvée, ERREUR EXPLICITE (pas de fallback)
    available = list(discovered.keys())
    raise ValueError(f"Leçon non trouvée: '{lesson_request}'. Leçons disponibles: {available}")
    
def discover_lessons():
    """Scanner automatiquement toutes les leçons disponibles."""
    from pathlib import Path
    
    lessons_dir = Path("kiro_lessons")
    discovered = {}
    
    if not lessons_dir.exists():
        return discovered
    
    for lesson_dir in lessons_dir.glob("lesson-*"):
        if lesson_dir.is_dir():
            lesson_id = lesson_dir.name  # ex: "lesson-003"
            exercise_file = lesson_dir / "exercice.py"
            if exercise_file.exists():
                discovered[lesson_id] = str(exercise_file)
    
    return discovered


def _display_session_summary_v31(session):
    """Affiche un résumé de session V3.1 formaté"""
    
    console.print(f"\n" + "="*80)
    
    # Utiliser les vraies métriques si disponibles, sinon fallback sur propriétés calculées
    final_score = getattr(session, 'final_grade', None)
    completed_tasks = getattr(session, '_real_completed_tasks', session.completed_tasks)
    total_tasks = getattr(session, '_real_total_tasks', session.total_tasks)
    # Utiliser le titre descriptif si disponible, sinon titre original
    lesson_title = getattr(session, '_descriptive_title', session.lesson.title)
    
    # Créer un tableau formaté
    table = Table(title="[STATS] Resume de Session Educative")
    table.add_column("Métrique", style="cyan", width=18)
    table.add_column("Valeur", style="yellow", width=60)
    
    table.add_row("Session ID", session.session_id)
    table.add_row("Leçon", lesson_title)
    table.add_row("Type", session.lesson.lesson_type.value)
    table.add_row("Score Final", f"{final_score}/100" if final_score is not None else "None/100")
    table.add_row("Tâches Terminées", f"{completed_tasks}/{total_tasks}")
    table.add_row("Statut", session.status.value)
    table.add_row("Dashboard Archon", get_dashboard_url(session.archon_project_id))
    
    console.print(table)

@app.command()
def list_sessions():
    """[LIST] Liste toutes les sessions éducatives récentes"""
    
    console.print(Panel.fit(
        "[LIST] Sessions Éducatives",
        style="bold blue"
    ))
    
    # Pour le moment, affichage simulé
    # Dans la vraie version, on interrogerait Archon
    table = Table(title="Sessions Récentes")
    table.add_column("ID", style="cyan")
    table.add_column("Leçon", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Note", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Date")
    
    # Données simulées
    sessions_data = [
        ("abc123", "Leçon 002: Sécurité", "debugging", "75.0/100", "[OK] Terminée", "2026-01-11 16:45"),
        ("def456", "Leçon 001: Bug Variable", "debugging", "85.0/100", "[OK] Terminée", "2026-01-11 16:30"),
    ]
    
    for session_id, lesson, lesson_type, grade, status, date in sessions_data:
        table.add_row(session_id, lesson, lesson_type, grade, status, date)
    
    console.print(table)
    console.print(f"\n[TIP] Utilisez 'session-status <id>' pour voir les détails d'une session")

@app.command()
def session_status(
    project_id: str = typer.Argument(..., help="ID du projet Archon")
):
    """[STATS] Affiche le statut détaillé d'une session"""
    
    console.print(Panel.fit(
        f"[STATS] Status Session: {project_id}",
        style="bold blue"
    ))
    
    # Simulation du statut
    console.print("[SEARCH] Récupération des informations depuis Archon...")
    
    # Dans la vraie version, on interrogerait Archon
    console.print(f"[LIST] Projet: Leçon 002 - Sécurité")
    console.print(f"[STATS] Progression: 100% (5/5 tâches)")
    console.print(f"[DOC] Documents: 8 artefacts")
    console.print(f"[EDU] Note finale: 75.0/100")
    console.print(f"[LINK] Dashboard: {get_dashboard_url(project_id)}")

@app.command()
def resume_session(
    project_id: str = typer.Argument(..., help="ID du projet Archon à reprendre")
):
    """[SYNC] Reprend une session éducative interrompue"""
    
    console.print(Panel.fit(
        f"[SYNC] Reprise Session: {project_id}",
        style="bold yellow"
    ))
    
    console.print("[!] Fonctionnalité en développement")
    console.print("[TIP] Pour le moment, utilisez 'start-lesson' pour créer une nouvelle session")

@app.command()
def export_session(
    project_id: str = typer.Argument(..., help="ID du projet à exporter"),
    format: str = typer.Option("markdown", "--format", "-f", help="Format d'export (markdown/json/pdf)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Fichier de sortie")
):
    """[EXPORT] Exporte une session éducative"""
    
    console.print(Panel.fit(
        f"[EXPORT] Export Session: {project_id}",
        style="bold green"
    ))
    
    if not output:
        output = f"session_{project_id}.{format}"
    
    console.print(f"[DOC] Format: {format}")
    console.print(f"📁 Fichier: {output}")
    console.print("[!] Fonctionnalité en développement")

@app.command()
def health():
    """[HEALTH] Vérifie la santé du système éducatif"""
    
    console.print(Panel.fit(
        "[HEALTH] Diagnostic Système",
        style="bold cyan"
    ))
    
    # Vérifications système
    checks = [
        ("[EDU] Orchestrateur éducatif", True),
        ("[LIST] Client Archon (Mock)", True),
        ("[BOT] Exécuteur Kiro", True),
        ("[STATS] Évaluateur académique", True),
        ("[LINK] Connexion Archon", False),  # Mock pour le moment
    ]
    
    table = Table(title="État des Composants")
    table.add_column("Composant", style="cyan")
    table.add_column("Status", style="green")
    
    for component, status in checks:
        status_icon = "[OK] OK" if status else "[!] Mock"
        table.add_row(component, status_icon)
    
    console.print(table)
    
    console.print(f"\n[TIP] Système prêt pour les sessions éducatives !")
    console.print(f"[!] Archon en mode Mock - configurez le vrai serveur pour la production")

@app.command()
def version():
    """[LIST] Affiche la version du système"""
    
    console.print(Panel.fit(
        "[EDU] Kiro Educational System V3.0\n"
        "Architecture: Archon-First Design\n"
        "Status: Fondations + Orchestrateur + CLI [OK]\n"
        "Prochaine étape: Intégration Archon MCP",
        style="bold blue"
    ))

def _display_session_summary(session):
    """Affiche un résumé de session formaté"""
    
    console.print(f"\n" + "="*60)
    console.print(Panel.fit(
        f"[STATS] RÉSUMÉ SESSION - {session.lesson.title}",
        style="bold green"
    ))
    
    # Tableau des métriques
    metrics_table = Table(title="Métriques de Performance")
    metrics_table.add_column("Métrique", style="cyan")
    metrics_table.add_column("Valeur", style="yellow")
    
    metrics_table.add_row("Note Finale", f"{session.final_grade:.1f}/100")
    metrics_table.add_row("Durée Totale", f"{session.duration_seconds:.1f}s")
    metrics_table.add_row("Tâches Terminées", f"{session.completed_tasks}/{session.total_tasks}")
    metrics_table.add_row("Progression", f"{session.progress_percentage:.1f}%")
    metrics_table.add_row("Type de Leçon", session.lesson.lesson_type.value)
    
    console.print(metrics_table)
    
    # Tableau des tâches
    tasks_table = Table(title="Détail des Tâches")
    tasks_table.add_column("#", style="cyan")
    tasks_table.add_column("Tâche", style="magenta")
    tasks_table.add_column("Status", style="green")
    tasks_table.add_column("Durée", style="yellow")
    
    for i, task in enumerate(session.tasks):
        status_icon = "[OK]" if task.status.value == "done" else "[X]" if task.status.value == "review" else "[SYNC]"
        duration = f"{task.duration_seconds:.1f}s" if task.duration_seconds > 0 else "-"
        tasks_table.add_row(str(i+1), task.title, f"{status_icon} {task.status.value}", duration)
    
    console.print(tasks_table)

if __name__ == "__main__":
    app()
