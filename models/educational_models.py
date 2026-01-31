"""
Modèles de données pour le système éducatif Kiro V3.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class LessonType(Enum):
    DEBUGGING = "debugging"
    SECURITY = "security"
    EXERCISE = "exercise"
    CSS = "css"
    TESTS = "tests"
    PATTERNS = "patterns"
    CLEAN_CODE = "clean_code"
    ARCHITECTURE = "architecture"
    UNKNOWN = "unknown"

class TaskType(Enum):
    ANALYZE = "analyze"
    EXECUTE = "execute"
    EVALUATE = "evaluate"
    ARCHIVE = "archive"
    REPORT = "report"

class SessionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStatus(Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    REVIEW = "review"

@dataclass
class Lesson:
    """Modèle d'une leçon éducative"""
    path: str
    title: str
    lesson_type: LessonType
    instructions: str
    reference_code: str
    expected_solution: Optional[str] = None
    lesson_number: Optional[str] = None
    difficulty: str = "beginner"
    estimated_duration: int = 30  # minutes
    
    @classmethod
    def from_path(cls, lesson_path: str) -> 'Lesson':
        """Crée une leçon à partir d'un chemin de fichier"""
        from pathlib import Path
        
        path = Path(lesson_path)
        lesson_dir = path.parent
        
        # Lire le README pour les instructions
        readme_path = lesson_dir / "README.md"
        instructions = ""
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                instructions = f.read()
        
        # Lire le code de référence
        reference_code = ""
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                reference_code = f.read()
        
        # Déterminer le type de leçon
        lesson_type = LessonType.UNKNOWN
        if "BUG" in instructions.upper() or "CORRIGER" in instructions.upper():
            lesson_type = LessonType.DEBUGGING
        elif "SECURITE" in instructions.upper() or "VULNERABILITE" in instructions.upper():
            lesson_type = LessonType.SECURITY
        elif "EXERCICE" in instructions.upper():
            lesson_type = LessonType.EXERCISE
        
        # Extraire le titre
        title = path.stem.replace("exercice", "").replace("_", " ").strip()
        if not title:
            title = f"Leçon {lesson_dir.name}"
        
        return cls(
            path=str(path),
            title=title,
            lesson_type=lesson_type,
            instructions=instructions,
            reference_code=reference_code,
            lesson_number=lesson_dir.name.split("-")[-1] if "-" in lesson_dir.name else None
        )

@dataclass
class EducationalTask:
    """Modèle d'une tâche éducative"""
    task_id: str
    task_type: TaskType
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    expected_artifacts: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    def start(self):
        """Marque la tâche comme commencée"""
        self.status = TaskStatus.DOING
        self.start_time = datetime.now()
    
    def complete(self, result: Dict[str, Any], success: bool = True):
        """Marque la tâche comme terminée"""
        self.status = TaskStatus.DONE if success else TaskStatus.REVIEW
        self.end_time = datetime.now()
        self.result = result
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def fail(self, error_message: str):
        """Marque la tâche comme échouée"""
        self.status = TaskStatus.TODO  # Reset pour retry
        self.end_time = datetime.now()
        self.result = {"success": False, "error": error_message}
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def is_completed(self) -> bool:
        """Vérifie si la tâche est terminée avec succès"""
        return self.status == TaskStatus.DONE

@dataclass
class EducationalSession:
    """Modèle d'une session éducative complète"""
    session_id: str
    lesson: Lesson
    student_name: str = "Kiro"
    instructor: str = "Professeur"
    session_start: datetime = field(default_factory=datetime.now)
    session_end: Optional[datetime] = None
    status: SessionStatus = SessionStatus.PENDING
    archon_project_id: Optional[str] = None
    tasks: List[EducationalTask] = field(default_factory=list)
    final_grade: Optional[float] = None
    dashboard_url: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Durée totale de la session"""
        if self.session_end and self.session_start:
            return (self.session_end - self.session_start).total_seconds()
        return 0.0
    
    @property
    def completed_tasks(self) -> int:
        """Nombre de tâches terminées"""
        return len([t for t in self.tasks if t.status == TaskStatus.DONE])
    
    @property
    def total_tasks(self) -> int:
        """Nombre total de tâches"""
        return len(self.tasks)
    
    @property
    def progress_percentage(self) -> float:
        """Pourcentage de progression"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    def add_task(self, task_type: TaskType, title: str, description: str) -> EducationalTask:
        """Ajoute une tâche à la session"""
        task_id = f"{self.session_id}_{task_type.value}_{len(self.tasks)+1}"
        task = EducationalTask(
            task_id=task_id,
            task_type=task_type,
            title=title,
            description=description
        )
        self.tasks.append(task)
        return task
    
    def complete_session(self, final_grade: float):
        """Termine la session"""
        self.session_end = datetime.now()
        self.final_grade = final_grade
        self.status = SessionStatus.COMPLETED
