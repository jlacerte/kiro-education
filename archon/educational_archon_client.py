"""Educational Archon Client.

HTTP client for Kiro Educational System to interact with Archon API.
Based on Project Orchestrator's ArchonClient.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel

# Configuration centralisee
from config.archon_config import ARCHON_API_URL, ARCHON_TIMEOUT

class _ArchonConfig:
    ARCHON_URL = ARCHON_API_URL
    HTTP_TIMEOUT = ARCHON_TIMEOUT

config = _ArchonConfig()


class EducationalProject(BaseModel):
    """Educational project model."""
    id: str
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EducationalTask(BaseModel):
    """Educational task model."""
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    status: str = "todo"  # todo, doing, review, done
    assignee: Optional[str] = None
    task_order: int = 0
    feature: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class EducationalArchonClient:
    """HTTP client for Archon API - Educational System.
    
    Provides methods to create and manage educational projects and tasks.
    """

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the client."""
        self.base_url = base_url or config.ARCHON_URL
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "EducationalArchonClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=config.HTTP_TIMEOUT)
        return self

    async def __aexit__(self, *args) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is available."""
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=config.HTTP_TIMEOUT)
        return self._client

    # ========== Project Methods ==========

    async def create_project(self, title: str, description: Optional[str] = None) -> EducationalProject:
        """Create a new educational project in Archon."""
        client = await self._ensure_client()
        
        payload = {
            "title": title,
            "description": description or f"Session éducative Kiro - {title}"
        }

        response = await client.post("/api/projects", json=payload)
        response.raise_for_status()

        data = response.json()
        project_data = data.get("project", data) if isinstance(data, dict) else data
        return EducationalProject.model_validate(project_data)

    async def get_project(self, project_id: str) -> EducationalProject:
        """Get a project by ID."""
        client = await self._ensure_client()
        
        response = await client.get(f"/api/projects/{project_id}")
        response.raise_for_status()
        
        data = response.json()
        project_data = data.get("project", data) if isinstance(data, dict) else data
        return EducationalProject.model_validate(project_data)

    # ========== Task Methods ==========

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        assignee: str = "Kiro",
        task_order: int = 0,
        feature: Optional[str] = None
    ) -> EducationalTask:
        """Create a new task in Archon."""
        client = await self._ensure_client()
        
        payload = {
            "project_id": project_id,
            "title": title,
            "description": description or f"Tâche éducative: {title}",
            "status": "todo",
            "assignee": assignee,
            "task_order": task_order,
            "feature": feature
        }

        response = await client.post("/api/tasks", json=payload)
        response.raise_for_status()

        data = response.json()
        task_data = data.get("task", data) if isinstance(data, dict) else data
        return EducationalTask.model_validate(task_data)

    async def update_task_status(self, task_id: str, status: str) -> EducationalTask:
        """Update task status (compatible PO)."""
        client = await self._ensure_client()
        
        payload = {"status": status}
        
        response = await client.put(f"/api/tasks/{task_id}", json=payload)
        response.raise_for_status()

        data = response.json()
        task_data = data.get("task", data) if isinstance(data, dict) else data
        return EducationalTask.model_validate(task_data)

    async def list_project_tasks(self, project_id: str) -> List[EducationalTask]:
        """List all tasks for a project."""
        client = await self._ensure_client()
        
        response = await client.get(f"/api/projects/{project_id}/tasks")
        response.raise_for_status()

        data = response.json()
        tasks_data = data.get("tasks", data) if isinstance(data, dict) else data
        
        return [EducationalTask.model_validate(task) for task in tasks_data]

    async def health_check(self) -> bool:
        """Check if Archon API is healthy."""
        try:
            client = await self._ensure_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    # ========== Document Methods (Compatible PO) ==========

    async def add_document(
        self,
        project_id: str,
        title: str,
        document_type: str,
        content: Dict[str, Any],
    ) -> bool:
        """Add a document to a project (compatible avec Project Orchestrator)."""
        client = await self._ensure_client()

        # Récupérer le projet actuel pour préserver les docs existants
        response = await client.get(f"/api/projects/{project_id}")
        response.raise_for_status()
        project_data = response.json()

        # Obtenir les docs existants ou liste vide
        existing_docs = project_data.get("docs", [])

        # Ajouter nouveau document avec champs requis
        now = datetime.now().isoformat()
        new_doc = {
            "id": str(uuid.uuid4()),
            "title": title,
            "document_type": document_type,
            "content": content,
            "created_at": now,
            "updated_at": now,
        }
        existing_docs.append(new_doc)

        # Mettre à jour le projet avec nouveaux docs
        update_response = await client.put(
            f"/api/projects/{project_id}",
            json={"docs": existing_docs},
        )
        update_response.raise_for_status()

        return True
