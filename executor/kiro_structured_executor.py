"""
Exécuteur Kiro structuré avec logging Archon intégré et prompts éducatifs
"""

import asyncio
import time
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

from kiro_executor import KiroExecutor, KiroExecutionResult
from archon.mock_educational_client import MockEducationalArchonClient

@dataclass
class StructuredResult:
    """Résultat structuré d'une exécution Kiro"""
    success: bool
    task_id: str
    execution_time: float
    files_created: List[str]
    files_modified: List[str]
    stdout: str
    stderr: str
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour Archon"""
        return {
            "success": self.success,
            "task_id": self.task_id,
            "execution_time": self.execution_time,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "stdout": self.stdout[:1000] + "..." if len(self.stdout) > 1000 else self.stdout,
            "stderr": self.stderr[:500] + "..." if len(self.stderr) > 500 else self.stderr,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "timestamp": datetime.now().isoformat()
        }

class KiroStructuredExecutor:
    """Executeur Kiro/Claude avec communication structuree, logging Archon et prompts educatifs"""

    def __init__(self, engine: str = "kiro"):
        self.engine = engine
        self.kiro_executor = KiroExecutor(engine=engine)
        self.archon_client: Optional[MockEducationalArchonClient] = None
        self.educational_prompts = self._load_educational_prompts()
    
    def _load_educational_prompts(self) -> Dict[str, str]:
        """Charge les prompts éducatifs depuis les fichiers"""
        prompts = {}
        prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
        
        prompt_files = {
            "worker": "kiro_educational_worker.md",
            "decomposer": "lesson_decomposer.md", 
            "fixer": "educational_fixer.md"
        }
        
        for key, filename in prompt_files.items():
            filepath = os.path.join(prompts_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    prompts[key] = f.read()
                print(f"[OK] Prompt {key} charge: {len(prompts[key])} caracteres")
            except FileNotFoundError:
                print(f"[!] Prompt {key} non trouve: {filepath}")
                prompts[key] = ""
            except Exception as e:
                print(f"[!] Prompt {key} erreur: {e}")
                prompts[key] = ""
        
        return prompts
    
    def get_educational_prompt(self, prompt_type: str, context: str = "") -> str:
        """Récupère un prompt éducatif avec contexte"""
        base_prompt = self.educational_prompts.get(prompt_type, "")
        if context:
            return f"{base_prompt}\n\n## CONTEXTE ÉDUCATIF\n{context}"
        return base_prompt
    
    def set_archon_client(self, client: MockEducationalArchonClient):
        """Configure le client Archon"""
        self.archon_client = client
    
    async def execute_educational_task(
        self, 
        task_id: str,
        project_id: str,
        lesson_context: str,
        task_type: str = "worker",
        agent: str = "blade-runner-fixed"
    ) -> StructuredResult:
        """Exécute une tâche éducative avec le prompt approprié"""
        
        # Construire le prompt éducatif
        educational_prompt = self.get_educational_prompt(task_type, lesson_context)
        
        print(f"🎓 Exécution tâche éducative ({task_type}): {task_id}")
        print(f"📚 Contexte: {lesson_context[:100]}...")
        
        return await self.execute_with_archon_logging(
            task_id, project_id, educational_prompt, agent
        )
    
    async def execute_with_archon_logging(
        self, 
        task_id: str,
        project_id: str,
        prompt: str,
        agent: str = "blade-runner-fixed"
    ) -> StructuredResult:
        """Exécute Kiro avec logging automatique dans Archon"""
        
        start_time = time.time()
        
        # Marquer tâche "doing" dans Archon
        if self.archon_client:
            await self.archon_client.update_task_status(task_id, "doing")
        
        try:
            # Exécuter Kiro
            print(f"🤖 Exécution Kiro: {prompt[:50]}...")
            result = await self._execute_kiro_structured(prompt, agent)
            
            # Logger résultat dans Archon
            if self.archon_client:
                await self.archon_client.add_document(
                    project_id,
                    f"Execution Log: {task_id}",
                    "execution_log",
                    result.to_dict()
                )
            
            # Marquer tâche "done" ou "review"
            status = "done" if result.success else "review"
            if self.archon_client:
                await self.archon_client.update_task_status(task_id, status)
            
            return result
            
        except Exception as e:
            # En cas d'erreur, créer un résultat d'échec
            execution_time = time.time() - start_time
            
            error_result = StructuredResult(
                success=False,
                task_id=task_id,
                execution_time=execution_time,
                files_created=[],
                files_modified=[],
                stdout="",
                stderr=str(e),
                metadata={},
                error_message=str(e)
            )
            
            # Logger l'erreur dans Archon
            if self.archon_client:
                await self.archon_client.add_document(
                    project_id,
                    f"Execution Error: {task_id}",
                    "execution_error",
                    error_result.to_dict()
                )
                await self.archon_client.update_task_status(task_id, "review")
            
            return error_result
    
    async def _execute_kiro_structured(self, prompt: str, agent: str) -> StructuredResult:
        """Exécute Kiro et structure le résultat"""
        
        start_time = time.time()
        
        try:
            # Utiliser notre exécuteur Kiro existant
            kiro_result = await self.kiro_executor.execute_task(
                task_description=prompt,
                agent=agent,
                timeout=300
            )
            
            execution_time = time.time() - start_time
            
            # Structurer le résultat
            structured_result = StructuredResult(
                success=kiro_result.success,
                task_id="",  # Sera rempli par l'appelant
                execution_time=execution_time,
                files_created=kiro_result.files_created,
                files_modified=kiro_result.files_modified,
                stdout=kiro_result.stdout or "",
                stderr=kiro_result.stderr or "",
                metadata={
                    "agent": agent,
                    "duration_seconds": kiro_result.duration_seconds,
                    "exit_code": getattr(kiro_result, 'exit_code', 0)
                },
                error_message=None if kiro_result.success else "Kiro execution failed"
            )
            
            structured_result.task_id = ""  # Sera rempli par l'appelant
            
            return structured_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return StructuredResult(
                success=False,
                task_id="",
                execution_time=execution_time,
                files_created=[],
                files_modified=[],
                stdout="",
                stderr=str(e),
                metadata={"agent": agent},
                error_message=str(e)
            )
    
    async def execute_debug_task(
        self, 
        task_id: str,
        project_id: str,
        lesson_path: str,
        lesson_type: str
    ) -> StructuredResult:
        """Exécute une tâche de débogage spécialisée"""
        
        if lesson_type == "security":
            prompt = f"""
MISSION DE SÉCURITÉ SPÉCIALISÉE:

Analysez le fichier {lesson_path} pour des vulnérabilités de sécurité.

VOTRE MISSION:
1. Identifiez TOUS les problèmes de sécurité
2. Corrigez chaque vulnérabilité trouvée
3. Assurez-vous qu'aucun secret n'est visible dans le code

CHERCHEZ SPÉCIFIQUEMENT:
- Tokens hardcodés
- Mots de passe en dur
- Fallbacks dangereux avec os.getenv()
- Secrets exposés côté client

Corrigez le fichier directement.
"""
        elif lesson_type == "debugging":
            prompt = f"""
MISSION DE DÉBOGAGE SPÉCIALISÉE:

Analysez et corrigez les bugs dans le fichier {lesson_path}.

VOTRE MISSION:
1. Exécutez le code pour identifier les erreurs
2. Analysez les exceptions et erreurs
3. Appliquez les corrections nécessaires
4. Validez que le code fonctionne après correction

Corrigez le fichier directement.
"""
        else:
            prompt = f"""
MISSION ÉDUCATIVE:

Analysez le fichier {lesson_path} et suivez les instructions fournies.

VOTRE MISSION:
1. Lisez attentivement les instructions
2. Implémentez la solution demandée
3. Respectez les critères de qualité
4. Testez votre solution

Créez les fichiers nécessaires selon les instructions.
"""
        
        return await self.execute_with_archon_logging(
            task_id, project_id, prompt
        )
