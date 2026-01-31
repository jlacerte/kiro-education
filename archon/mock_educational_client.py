"""
Client Archon éducatif - Version Mock pour développement
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Optional
from models.educational_models import Lesson, EducationalSession, EducationalTask, TaskStatus
from config.archon_config import ARCHON_API_URL

class MockEducationalArchonClient:
    """Client Archon simulé pour développement sans serveur"""

    def __init__(self):
        self.projects: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}
        self.documents: Dict[str, List[Dict]] = {}
        self.base_url = ARCHON_API_URL
    
    async def create_educational_project(self, lesson: Lesson) -> str:
        """Crée un projet Archon pour une leçon"""
        project_id = str(uuid.uuid4())
        
        project_data = {
            "id": project_id,
            "title": f"Leçon {lesson.lesson_number or 'X'}: {lesson.title}",
            "description": f"Session d'apprentissage Kiro - {lesson.lesson_type.value}",
            "created_at": datetime.now().isoformat(),
            "lesson_path": lesson.path,
            "lesson_type": lesson.lesson_type.value,
            "student": "Kiro",
            "instructor": "Professeur"
        }
        
        self.projects[project_id] = project_data
        self.documents[project_id] = []
        
        print(f"📋 Projet Archon créé: {project_id}")
        print(f"   Titre: {project_data['title']}")
        print(f"   Type: {lesson.lesson_type.value}")
        
        return project_id
    
    async def create_educational_tasks(self, project_id: str, lesson: Lesson, custom_task_titles: Optional[List[str]] = None) -> List[str]:
        """Crée les tâches éducatives (standard ou personnalisées)"""
        
        if custom_task_titles:
            # Utiliser les tâches personnalisées du TaskDecomposer
            tasks_data = []
            for i, title in enumerate(custom_task_titles):
                tasks_data.append((f"task_{i}", title, f"Tâche éducative adaptée: {title}"))
        else:
            # Utiliser les tâches standard (fallback)
            tasks_data = [
                ("analyze", "Analyser les instructions de la leçon", "Lecture et compréhension du contexte éducatif"),
                ("execute", "Exécuter Kiro en mode approprié", f"Lancement de Kiro en mode {lesson.lesson_type.value}"),
                ("evaluate", "Évaluer la performance de Kiro", "Assessment académique multi-dimensionnel"),
                ("archive", "Archiver solutions et artefacts", "Sauvegarde des fichiers créés par Kiro"),
                ("report", "Générer le bulletin académique", "Création du rapport final de performance")
            ]
        
        task_ids = []
        
        for i, (task_type, title, description) in enumerate(tasks_data):
            task_id = str(uuid.uuid4())
            
            task_data = {
                "id": task_id,
                "project_id": project_id,
                "title": title,
                "description": description,
                "task_type": task_type,
                "status": "todo",
                "task_order": (len(tasks_data) - i) * 10,  # Ordre décroissant
                "assignee": "Kiro Educational System",
                "created_at": datetime.now().isoformat()
            }
            
            self.tasks[task_id] = task_data
            task_ids.append(task_id)
        
        print(f"📋 {len(task_ids)} tâches créées pour le projet {project_id}")
        for i, (task_type, title, _) in enumerate(tasks_data):
            print(f"   {i+1}. {title}")
        
        return task_ids
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Met à jour le statut d'une tâche"""
        if task_id in self.tasks:
            old_status = self.tasks[task_id]["status"]
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            task_title = self.tasks[task_id]["title"]
            print(f"📊 Tâche mise à jour: {task_title}")
            print(f"   Status: {old_status} → {status}")
            
            return True
        return False
    
    async def add_document(
        self, 
        project_id: str, 
        title: str, 
        document_type: str, 
        content: Dict[str, Any]
    ) -> bool:
        """Ajoute un document au projet"""
        
        document = {
            "id": str(uuid.uuid4()),
            "title": title,
            "document_type": document_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if project_id not in self.documents:
            self.documents[project_id] = []
        
        self.documents[project_id].append(document)
        
        print(f"📄 Document ajouté: {title}")
        print(f"   Type: {document_type}")
        print(f"   Taille: {len(str(content))} caractères")
        
        return True
    
    async def save_lesson_artifacts(self, project_id: str, artifacts: Dict[str, Any]):
        """Sauvegarde tous les artefacts de la leçon"""
        
        # Sauvegarder chaque type d'artefact
        for artifact_type, artifact_data in artifacts.items():
            await self.add_document(
                project_id,
                f"Artefact: {artifact_type}",
                artifact_type,
                artifact_data
            )
        
        print(f"💾 {len(artifacts)} artefacts sauvegardés dans le projet {project_id}")
    
    async def get_session_dashboard_url(self, project_id: str) -> str:
        """Retourne l'URL du dashboard pour cette session"""
        dashboard_url = f"{self.base_url}/projects/{project_id}"
        
        print(f"🔗 Dashboard URL: {dashboard_url}")
        
        return dashboard_url
    
    async def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Retourne un résumé du projet"""
        if project_id not in self.projects:
            return {}
        
        project = self.projects[project_id]
        project_tasks = [t for t in self.tasks.values() if t["project_id"] == project_id]
        project_documents = self.documents.get(project_id, [])
        
        completed_tasks = len([t for t in project_tasks if t["status"] == "done"])
        total_tasks = len(project_tasks)
        
        return {
            "project": project,
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "progress": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "documents": len(project_documents),
            "dashboard_url": await self.get_session_dashboard_url(project_id)
        }
    
    def print_session_summary(self, project_id: str):
        """Affiche un résumé de la session (pour debug)"""
        if project_id not in self.projects:
            print(f"❌ Projet {project_id} non trouvé")
            return
        
        project = self.projects[project_id]
        project_tasks = [t for t in self.tasks.values() if t["project_id"] == project_id]
        project_documents = self.documents.get(project_id, [])
        
        print(f"\n📊 RÉSUMÉ SESSION - {project['title']}")
        print(f"{'='*60}")
        print(f"📋 Tâches: {len([t for t in project_tasks if t['status'] == 'done'])}/{len(project_tasks)} terminées")
        print(f"📄 Documents: {len(project_documents)} artefacts")
        print(f"🔗 Dashboard: {self.base_url}/projects/{project_id}")
        
        print(f"\n📋 Détail des tâches:")
        for task in sorted(project_tasks, key=lambda x: x["task_order"], reverse=True):
            status_icon = "✅" if task["status"] == "done" else "🔄" if task["status"] == "doing" else "⏳"
            print(f"   {status_icon} {task['title']}")
        
        print(f"\n📄 Documents générés:")
        for doc in project_documents:
            print(f"   📄 {doc['title']} ({doc['document_type']})")


# Instance globale pour développement
mock_archon = MockEducationalArchonClient()
