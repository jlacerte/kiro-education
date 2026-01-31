#!/usr/bin/env python3
"""
Kiro Orchestrator - Phase 2.1: KiroExecutor
Wrapper sophistiqué autour de Kiro CLI avec parsing intelligent
"""

import asyncio
import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

@dataclass
class KiroExecutionResult:
    """Résultat d'une exécution Kiro CLI avec parsing intelligent"""
    
    # Résultat de base
    success: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: int = -1
    duration_seconds: float = 0.0
    
    # Parsing intelligent
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    directories_created: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)
    
    # Métadonnées Kiro
    agent_used: Optional[str] = None
    model_used: Optional[str] = None
    credits_used: Optional[float] = None
    session_id: Optional[str] = None
    
    # Analyse du contenu
    task_summary: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

class KiroOutputParser:
    """Parse la sortie de Kiro CLI pour extraire des informations structurées"""
    
    def __init__(self):
        # Patterns pour détecter les actions
        self.file_patterns = {
            'created': [
                r"Creating:\s+(.+)",
                r"Created file:\s+(.+)",
                r"File created.*?:\s+(.+)",
                r"Writing to:\s+(.+)",
                r"Saved to:\s+(.+)"
            ],
            'modified': [
                r"Modified:\s+(.+)",
                r"Updated:\s+(.+)",
                r"Editing:\s+(.+)",
                r"Changed:\s+(.+)"
            ],
            'directory': [
                r"Created directory:\s+(.+)",
                r"mkdir\s+(.+)",
                r"Making directory:\s+(.+)"
            ]
        }
        
        # Patterns pour métadonnées
        self.metadata_patterns = {
            'credits': r"Credits:\s+([\d.]+)",
            'time': r"Time:\s+([\d.]+)s",
            'model': r"Model:\s+(.+?)(?:\s|$)",
            'agent': r"\[(.+?)\]"
        }
        
        # Patterns pour erreurs et warnings
        self.error_patterns = [
            r"Error:\s+(.+)",
            r"❌\s+(.+)",
            r"Failed:\s+(.+)",
            r"Exception:\s+(.+)"
        ]
        
        self.warning_patterns = [
            r"Warning:\s+(.+)",
            r"⚠️\s+(.+)",
            r"Note:\s+(.+)"
        ]
    
    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse la sortie complète de Kiro CLI"""
        
        # Combiner stdout et stderr pour l'analyse
        full_output = f"{stdout}\n{stderr}"
        
        # Extraire les fichiers
        files_created = self._extract_files(full_output, 'created')
        files_modified = self._extract_files(full_output, 'modified')
        directories_created = self._extract_files(full_output, 'directory')
        
        # Extraire les métadonnées
        metadata = self._extract_metadata(full_output)
        
        # Extraire erreurs et warnings
        errors = self._extract_patterns(full_output, self.error_patterns)
        warnings = self._extract_patterns(full_output, self.warning_patterns)
        
        # Générer un résumé de tâche
        task_summary = self._generate_task_summary(files_created, files_modified, directories_created)
        
        return {
            'files_created': files_created,
            'files_modified': files_modified,
            'directories_created': directories_created,
            'agent_used': metadata.get('agent'),
            'model_used': metadata.get('model'),
            'credits_used': metadata.get('credits'),
            'task_summary': task_summary,
            'error_message': errors[0] if errors else None,
            'warnings': warnings
        }
    
    def _extract_files(self, text: str, category: str) -> List[str]:
        """Extrait les fichiers d'une catégorie donnée"""
        files = []
        patterns = self.file_patterns.get(category, [])
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Nettoyer le chemin (enlever les codes ANSI, etc.)
                clean_path = re.sub(r'\x1b\[[0-9;]*m', '', match).strip()
                if clean_path and clean_path not in files:
                    files.append(clean_path)
        
        return files
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extrait les métadonnées de la sortie"""
        metadata = {}
        
        for key, pattern in self.metadata_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if key == 'credits':
                    try:
                        metadata[key] = float(value)
                    except ValueError:
                        pass
                else:
                    metadata[key] = value
        
        return metadata
    
    def _extract_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Extrait les matches pour une liste de patterns"""
        results = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                clean_match = re.sub(r'\x1b\[[0-9;]*m', '', match).strip()
                if clean_match and clean_match not in results:
                    results.append(clean_match)
        
        return results
    
    def _generate_task_summary(self, created: List[str], modified: List[str], directories: List[str]) -> str:
        """Génère un résumé de ce qui a été fait"""
        actions = []
        
        if created:
            actions.append(f"Created {len(created)} file(s): {', '.join(created[:3])}")
            if len(created) > 3:
                actions[-1] += f" and {len(created) - 3} more"
        
        if modified:
            actions.append(f"Modified {len(modified)} file(s): {', '.join(modified[:3])}")
            if len(modified) > 3:
                actions[-1] += f" and {len(modified) - 3} more"
        
        if directories:
            actions.append(f"Created {len(directories)} directory(ies): {', '.join(directories)}")
        
        return "; ".join(actions) if actions else "No file operations detected"

class KiroExecutor:
    """Executeur sophistique pour Kiro/Claude CLI avec parsing intelligent"""

    def __init__(self, default_agent: Optional[str] = None, default_timeout: int = 300, engine: str = "kiro"):
        self.default_agent = default_agent
        self.default_timeout = default_timeout
        self.engine = engine  # "kiro" ou "claude"
        self.parser = KiroOutputParser()
        self.logger = logging.getLogger(__name__)
    
    async def execute_task(
        self,
        task_description: str,
        agent: Optional[str] = None,
        timeout: Optional[int] = None,
        trust_all_tools: bool = True,
        working_directory: Optional[Path] = None
    ) -> KiroExecutionResult:
        """Exécute une tâche Kiro CLI avec parsing intelligent"""
        
        start_time = time.time()
        
        # Préparer la commande
        cmd = self._build_command(
            agent or self.default_agent,
            trust_all_tools
        )
        
        # Préparer l'environnement
        cwd = working_directory or Path.cwd()
        timeout_value = timeout or self.default_timeout
        
        engine_name = "Claude" if self.engine == "claude" else "Kiro"
        self.logger.info(f"[{engine_name.upper()}] Executing task: {task_description[:50]}...")
        self.logger.debug(f"Working directory: {cwd}")

        # Pour Claude: utiliser fichier temp (limite Windows 8191 chars)
        import tempfile
        import os
        temp_file = None

        try:
            if self.engine == "claude":
                # Ecrire le prompt dans un fichier temp
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(task_description)
                    temp_file = f.name
                cmd = self._build_command(agent or self.default_agent, trust_all_tools, prompt_file=temp_file)
                self.logger.debug(f"Command: {cmd[-1][:100]}...")

                # Claude: utiliser shell pour le pipe
                process = await asyncio.create_subprocess_shell(
                    cmd[-1],  # La commande complete avec pipe
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_value
                )
            else:
                # Kiro: stdin classique
                self.logger.debug(f"Command: {' '.join(cmd)}")
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=task_description.encode('utf-8')),
                    timeout=timeout_value
                )
            
            # Calculer la durée
            duration = time.time() - start_time
            
            # Décoder les sorties
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Parser la sortie
            parsed_data = self.parser.parse_output(stdout_text, stderr_text)
            
            # Créer le résultat
            result = KiroExecutionResult(
                success=(process.returncode == 0),
                stdout=stdout_text,
                stderr=stderr_text,
                exit_code=process.returncode,
                duration_seconds=duration,
                **parsed_data
            )
            
            # Log du resultat
            if result.success:
                self.logger.info(f"[OK] Task completed in {duration:.1f}s: {result.task_summary}")
            else:
                self.logger.error(f"[FAIL] Task failed in {duration:.1f}s: {result.error_message}")
            
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.logger.error(f"[TIMEOUT] Task timed out after {timeout_value}s")
            
            return KiroExecutionResult(
                success=False,
                exit_code=-1,
                duration_seconds=duration,
                error_message=f"Task timed out after {timeout_value} seconds"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"[ERROR] Task failed with exception: {e}")

            return KiroExecutionResult(
                success=False,
                exit_code=-1,
                duration_seconds=duration,
                error_message=str(e)
            )

        finally:
            # Nettoyer le fichier temp (Claude)
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

    def _build_command(self, agent: Optional[str], trust_all_tools: bool, prompt_file: Optional[str] = None) -> List[str]:
        """Construit la commande Kiro ou Claude CLI"""
        if self.engine == "claude":
            # Claude: utilise pipe depuis fichier temp (evite limite Windows 8191 chars)
            if prompt_file:
                # Windows: type file | claude
                cmd = ["cmd", "/c", f'type "{prompt_file}" | claude --dangerously-skip-permissions']
                if agent:
                    cmd[-1] += f" --agent {agent}"
                return cmd
            else:
                cmd = ["claude", "--dangerously-skip-permissions"]
                if agent:
                    cmd.extend(["--agent", agent])
                return cmd
        else:
            # Kiro: stdin classique
            cmd = ["kiro-cli", "chat", "--no-interactive"]
            if trust_all_tools:
                cmd.append("--trust-all-tools")
            if agent:
                cmd.extend(["--agent", agent])
            return cmd
    
    # Méthode synchrone pour compatibilité
    def execute_task_sync(
        self,
        task_description: str,
        agent: Optional[str] = None,
        timeout: Optional[int] = None,
        trust_all_tools: bool = True,
        working_directory: Optional[Path] = None
    ) -> KiroExecutionResult:
        """Version synchrone de execute_task"""
        return asyncio.run(self.execute_task(
            task_description, agent, timeout, trust_all_tools, working_directory
        ))

# Configuration du logging
def setup_logging(level: str = "INFO"):
    """Configure le logging pour KiroExecutor"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"kiro-executor-{int(time.time())}.log")
        ]
    )

# Exemple d'utilisation
async def main():
    """Exemple d'utilisation du KiroExecutor"""
    
    setup_logging("INFO")
    
    executor = KiroExecutor(
        default_agent="blade-runner-fixed",
        default_timeout=60
    )
    
    # Test simple
    result = await executor.execute_task(
        "Create a file named 'executor-test.txt' with content 'KiroExecutor works!'"
    )
    
    print(f"\n🎯 RÉSULTAT D'EXÉCUTION")
    print(f"✅ Succès: {result.success}")
    print(f"⏱️  Durée: {result.duration_seconds:.1f}s")
    print(f"📁 Fichiers créés: {result.files_created}")
    print(f"🤖 Agent: {result.agent_used}")
    print(f"📝 Résumé: {result.task_summary}")
    
    if result.error_message:
        print(f"❌ Erreur: {result.error_message}")
    
    if result.warnings:
        print(f"⚠️  Warnings: {result.warnings}")

if __name__ == "__main__":
    asyncio.run(main())
