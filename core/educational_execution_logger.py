"""
Système de logging en temps réel pour les sessions éducatives Kiro.
Capture les détails d'exécution pour améliorer la traçabilité et le débogage.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LogEntry:
    """Entrée de log avec timestamp et détails."""
    timestamp: datetime
    message: str
    level: str = "INFO"  # INFO, SUCCESS, ERROR, DEBUG
    task_id: Optional[str] = None
    duration: Optional[float] = None
    tokens: Optional[int] = None
    cost: Optional[float] = None


class ExecutionLogger:
    """Logger temps réel pour sessions éducatives."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entries: List[LogEntry] = []
        self.session_start = datetime.now()
        self.current_task_start: Optional[datetime] = None
        
        # Log de démarrage
        self.log_info("[EDU] Session éducative démarrée")
    
    def log_info(self, message: str, **kwargs):
        """Log d'information générale."""
        self._add_entry(message, "INFO", **kwargs)
    
    def log_success(self, message: str, **kwargs):
        """Log de succès avec [OK]."""
        self._add_entry(f"[OK] {message}", "SUCCESS", **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log d'erreur avec [X]."""
        self._add_entry(f"[X] {message}", "ERROR", **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log de débogage avec [FIX]."""
        self._add_entry(f"[FIX] {message}", "DEBUG", **kwargs)
    
    def log_task_start(self, task_title: str, task_id: str):
        """Marquer le début d'une tâche."""
        self.current_task_start = datetime.now()
        self.log_info(f"[SYNC] Début: {task_title}", task_id=task_id)
    
    def log_task_complete(self, task_title: str, task_id: str, tokens: int = 0, cost: float = 0.0):
        """Marquer la fin d'une tâche avec métriques."""
        duration = None
        if self.current_task_start:
            duration = (datetime.now() - self.current_task_start).total_seconds() / 60
        
        metrics = f"({duration:.2f}min" if duration else "("
        if tokens > 0:
            metrics += f", {tokens} tokens"
        if cost > 0:
            metrics += f", ${cost:.4f}"
        metrics += ")"
        
        self.log_success(f"{task_title} {metrics}", 
                        task_id=task_id, duration=duration, tokens=tokens, cost=cost)
        self.current_task_start = None
    
    def log_bug_detected(self, bug_description: str):
        """Logger une erreur détectée dans le code."""
        self.log_info(f"[BUG] Bug détecté: {bug_description}")
    
    def log_code_correction(self, correction_description: str):
        """Logger une correction de code appliquée."""
        self.log_success(f"[FIX] Correction: {correction_description}")
    
    def _add_entry(self, message: str, level: str, **kwargs):
        """Ajouter une entrée au log."""
        entry = LogEntry(
            timestamp=datetime.now(),
            message=message,
            level=level,
            **kwargs
        )
        self.entries.append(entry)
    
    def get_formatted_log(self, total_tasks: int = 0, final_score: int = 0) -> str:
        """Générer le log formaté en markdown."""
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60
        
        # En-tête
        log_content = f"""# Execution Log - Session {self.session_id}

*Généré le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}*

## [RUN] Workflow Execution

"""
        
        # Entrées chronologiques
        for entry in self.entries:
            time_str = entry.timestamp.strftime('%H:%M:%S')
            log_content += f"- **{time_str}** - {entry.message}\n"
        
        # Résumé final
        log_content += f"""
## [STATS] Session Summary

- **Durée totale**: {session_duration:.2f} minutes
- **Tâches traitées**: {total_tasks}
- **Score final**: {final_score}/100
- **Entrées de log**: {len(self.entries)}

## [TARGET] Metriques Detaillees

"""
        
        # Métriques par tâche
        task_entries = [e for e in self.entries if e.task_id and e.duration]
        if task_entries:
            total_tokens = sum(e.tokens or 0 for e in task_entries)
            total_cost = sum(e.cost or 0 for e in task_entries)
            
            log_content += f"- **Tokens totaux**: {total_tokens:,}\n"
            log_content += f"- **Coût estimé**: ${total_cost:.4f}\n"
            log_content += f"- **Durée moyenne par tâche**: {session_duration/max(total_tasks, 1):.2f} min\n"
        
        log_content += f"""
---

*Log généré automatiquement par Kiro Educational System V3.2*
*Système de logging temps réel - Pour le directeur qui part en vacances [VACATION]*
"""
        
        return log_content
