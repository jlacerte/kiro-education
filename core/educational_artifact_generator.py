"""Educational Artifact Generator.

Generates educational session artifacts based on Project Orchestrator's ArtifactGenerator.
Creates standardized lesson output structure with backup, final code, certificate, and artifacts.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console

console = Console()

class EducationalArtifactGenerator:
    """Generates educational session artifacts and folder structure."""
    
    def __init__(self, base_dir: str = "kiro_courses"):
        """Initialize the generator.
        
        Args:
            base_dir: Base directory for educational outputs.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_session_folder(self, lesson_number: str, lesson_type: str) -> Path:
        """Create timestamped session folder.
        
        Args:
            lesson_number: Lesson identifier (e.g., "lesson-001")
            lesson_type: Type of lesson (e.g., "debugging")
            
        Returns:
            Path to created session folder.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
        folder_name = f"{lesson_number}_{lesson_type}_{timestamp}"
        
        session_path = self.base_dir / folder_name
        session_path.mkdir(exist_ok=True)
        
        # Create standard subdirectories
        (session_path / "00_backup_original").mkdir(exist_ok=True)
        (session_path / "01_code_final").mkdir(exist_ok=True)
        (session_path / "02_certificat").mkdir(exist_ok=True)
        (session_path / "03_artifacts").mkdir(exist_ok=True)
        
        console.print(f"[DIR] Session folder created: {folder_name}")
        return session_path
    
    def save_original_code(self, session_path: Path, lesson_path: str) -> None:
        """Save original lesson code to backup folder.
        
        Args:
            session_path: Path to session folder.
            lesson_path: Path to original lesson file.
        """
        backup_dir = session_path / "00_backup_original"
        
        if Path(lesson_path).exists():
            shutil.copy2(lesson_path, backup_dir / "exercice.py")
            console.print("[SAVE] Original code backed up")
    
    def save_final_code(self, session_path: Path, corrected_code: str) -> None:
        """Save corrected code to final folder.
        
        Args:
            session_path: Path to session folder.
            corrected_code: Corrected Python code.
        """
        final_dir = session_path / "01_code_final"
        final_file = final_dir / "exercice_corrige.py"
        
        final_file.write_text(corrected_code, encoding="utf-8")
        console.print("[OK] Final code saved")
    
    def generate_certificate(self, session_path: Path, session_data: Dict[str, Any]) -> None:
        """Generate completion certificate.
        
        Args:
            session_path: Path to session folder.
            session_data: Session information for certificate.
        """
        cert_dir = session_path / "02_certificat"
        timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
        cert_file = cert_dir / f"CERTIFICAT_KIRO_{session_data.get('lesson_number', '001')}_{timestamp}.md"
        
        certificate_content = f"""# [EDU] Certificat de Réussite Kiro Educational System

[!] **VERSION PROTOTYPE - CORRECTIONS LIMITÉES** [!]

## Session Information
- **Leçon**: {session_data.get('lesson_title', 'N/A')}
- **Type**: {session_data.get('lesson_type', 'N/A')}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Session ID**: {session_data.get('session_id', 'N/A')}

## Résultats
- **Score Final**: {session_data.get('final_score', 'N/A')}/100
- **Tâches Terminées**: {session_data.get('completed_tasks', 0)}/{session_data.get('total_tasks', 0)}
- **Statut**: {session_data.get('status', 'completed').upper()}

## Métriques de Performance
- **Durée**: {session_data.get('duration', 'N/A')} minutes
- **Projet Archon**: {session_data.get('archon_project_id', 'N/A')}

## Avertissement Prototype

[!] **Cette version est un prototype de système éducatif**
- Les corrections de code sont limitées ou non fonctionnelles
- Le système excelle en infrastructure de reporting
- Développement du moteur de correction en cours

---

*Certificat généré automatiquement par Kiro Educational System V3.2 - PROTOTYPE*
*Système d'apprentissage autonome - Intelligence Artificielle*
"""
        
        cert_file.write_text(certificate_content, encoding="utf-8")
        console.print("[TROPHY] Certificate generated")
    
    def save_execution_log(self, session_path: Path, execution_log: str) -> None:
        """Save execution log to artifacts.
        
        Args:
            session_path: Path to session folder.
            execution_log: Execution log content.
        """
        artifacts_dir = session_path / "03_artifacts"
        log_file = artifacts_dir / "execution_log.md"
        
        log_content = f"""# Execution Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Session Execution Details

{execution_log}

---

*Log généré par Kiro Educational System V3.2*
"""
        
        log_file.write_text(log_content, encoding="utf-8")
        console.print("[LIST] Execution log saved")
    
    def save_session_metrics(self, session_path: Path, metrics: Dict[str, Any]) -> None:
        """Save session metrics to artifacts.
        
        Args:
            session_path: Path to session folder.
            metrics: Session metrics data.
        """
        artifacts_dir = session_path / "03_artifacts"
        metrics_file = artifacts_dir / "session_metrics.json"
        
        import json
        metrics_file.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print("[STATS] Session metrics saved")
    
    def generate_session_artifacts(
        self,
        lesson_number: str,
        lesson_type: str,
        lesson_path: str,
        session_data: Dict[str, Any],
        corrected_code: Optional[str] = None,
        execution_log: Optional[str] = None
    ) -> Path:
        """Generate complete session artifacts.
        
        Args:
            lesson_number: Lesson identifier.
            lesson_type: Type of lesson.
            lesson_path: Path to original lesson.
            session_data: Session information.
            corrected_code: Corrected code (if any).
            execution_log: Execution log.
            
        Returns:
            Path to session folder.
        """
        # Create session folder
        session_path = self.create_session_folder(lesson_number, lesson_type)
        
        # Save original code
        self.save_original_code(session_path, lesson_path)
        
        # Save corrected code if available
        if corrected_code:
            self.save_final_code(session_path, corrected_code)
        
        # Generate certificate
        self.generate_certificate(session_path, session_data)
        
        # Save execution log
        if execution_log:
            self.save_execution_log(session_path, execution_log)
        
        # Save metrics
        self.save_session_metrics(session_path, session_data)
        
        console.print(f"[SUCCESS] Session artifacts complete: {session_path.name}")
        return session_path
