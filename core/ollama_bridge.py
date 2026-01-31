"""Ollama Bridge for WSL to Windows communication.

Since WSL cannot directly access Windows localhost due to firewall,
this bridge uses PowerShell as an intermediary.
"""

import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Import GPU Monitor pour prévention crash
try:
    from core.gpu_monitor import log_gpu_status, check_vram_safe, get_gpu_stats
    GPU_MONITOR_AVAILABLE = True
except ImportError:
    GPU_MONITOR_AVAILABLE = False

# Logger pour l'audit Ollama
logger = logging.getLogger("ollama_validateur")
logger.setLevel(logging.DEBUG)


class OllamaBridge:
    """Bridge to communicate with Ollama running on Windows from WSL."""

    def __init__(self, model: str = "llama3.1:latest"):
        """Initialize the bridge with a default model.

        Args:
            model: The Ollama model to use (default: llama3.1:latest)
        """
        self.model = model
        self.base_url = "http://localhost:11434"

    def _run_powershell(self, script: str, timeout: int = 60) -> Optional[str]:
        """Execute a PowerShell script and return the output.

        Args:
            script: The PowerShell script to execute
            timeout: Timeout in seconds

        Returns:
            The output string or None if failed
        """
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", script],
                capture_output=True,
                timeout=timeout
            )
            if result.returncode == 0:
                # Try multiple encodings
                for encoding in ['utf-8', 'cp1252', 'latin-1']:
                    try:
                        return result.stdout.decode(encoding).strip()
                    except UnicodeDecodeError:
                        continue
                # Fallback: decode with errors ignored
                return result.stdout.decode('utf-8', errors='ignore').strip()
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                print(f"PowerShell error: {error_msg}")
                return None
        except subprocess.TimeoutExpired:
            print(f"PowerShell timeout after {timeout}s")
            return None
        except Exception as e:
            print(f"PowerShell exception: {e}")
            return None

    def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models.

        Returns:
            List of model dictionaries with name, size, etc.
        """
        script = f"""
        $response = Invoke-RestMethod -Uri '{self.base_url}/api/tags' -Method Get
        $response.models | ForEach-Object {{
            [PSCustomObject]@{{
                name = $_.name
                size_gb = [math]::Round($_.size / 1GB, 2)
                family = $_.details.family
                parameters = $_.details.parameter_size
            }}
        }} | ConvertTo-Json
        """
        output = self._run_powershell(script)
        if output:
            try:
                models = json.loads(output)
                # Handle single model case (not a list)
                if isinstance(models, dict):
                    models = [models]
                return models
            except json.JSONDecodeError:
                return []
        return []

    def generate(self, prompt: str, system: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 500,
                 seed: Optional[int] = None, top_k: Optional[int] = None) -> Optional[str]:
        """Generate a response from Ollama.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            seed: Optional random seed for reproducibility
            top_k: Optional top-k sampling (1 = greedy/deterministic)

        Returns:
            The generated response or None if failed
        """
        import tempfile
        import os

        # Build the request body as Python dict
        options = {
            "temperature": temperature,
            "num_predict": max_tokens
        }

        # Add deterministic parameters if specified
        if seed is not None:
            options["seed"] = seed
        if top_k is not None:
            options["top_k"] = top_k

        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }

        if system:
            body["system"] = system

        # Write JSON to temp file (avoids PowerShell escaping issues)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False,
                                         encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False)
            temp_path = f.name

        # Convert WSL path to Windows path
        win_path = temp_path.replace('/tmp/', 'C:/Users/').replace('/', '\\\\')
        # Actually use wslpath
        try:
            wsl_result = subprocess.run(['wslpath', '-w', temp_path],
                                       capture_output=True, text=True)
            win_path = wsl_result.stdout.strip()
        except:
            pass

        script = f"""
        $body = Get-Content -Path '{win_path}' -Raw -Encoding UTF8
        $response = Invoke-RestMethod -Uri '{self.base_url}/api/generate' -Method Post -Body $body -ContentType 'application/json; charset=utf-8'
        $response.response
        """

        try:
            result = self._run_powershell(script, timeout=120)
            return result
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

    def chat(self, messages: List[Dict[str, str]],
             temperature: float = 0.7) -> Optional[str]:
        """Have a chat conversation with Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature

        Returns:
            The assistant's response or None if failed
        """
        messages_json = json.dumps(messages)

        script = f"""
        $body = @{{
            model = '{self.model}'
            messages = {messages_json} | ConvertFrom-Json
            stream = $false
            options = @{{
                temperature = {temperature}
            }}
        }} | ConvertTo-Json -Depth 10

        $response = Invoke-RestMethod -Uri '{self.base_url}/api/chat' -Method Post -Body $body -ContentType 'application/json'
        $response.message.content
        """

        return self._run_powershell(script, timeout=120)

    def is_available(self) -> bool:
        """Check if Ollama is available.

        Returns:
            True if Ollama is reachable
        """
        script = f"""
        try {{
            $response = Invoke-RestMethod -Uri '{self.base_url}/api/tags' -Method Get -TimeoutSec 5
            'OK'
        }} catch {{
            'FAIL'
        }}
        """
        result = self._run_powershell(script, timeout=10)
        return result == "OK"


class CanardSocratique:
    """The Socratic Rubber Duck - an AI that only asks questions."""

    SYSTEM_PROMPT = """Tu es un Canard en Caoutchouc Intelligent, un compagnon d'apprentissage pour les étudiants en programmation.

RÈGLES ABSOLUES:
1. Tu ne donnes JAMAIS la réponse directement
2. Tu réponds UNIQUEMENT par des questions socratiques
3. Tu guides l'étudiant vers la découverte par lui-même
4. Tu es bienveillant, patient et encourageant
5. Tes questions doivent être progressives et adaptées au niveau

EXEMPLES DE BONNES QUESTIONS:
- "Qu'est-ce que tu observes quand tu exécutes ce code?"
- "Que signifie ce message d'erreur selon toi?"
- "À quel moment ta variable devrait-elle être définie?"
- "Qu'est-ce qui se passe si tu ajoutes un print() ici?"

EXEMPLES DE CE QU'IL NE FAUT PAS FAIRE:
- "Le bug est à la ligne 5" (réponse directe)
- "Tu dois ajouter une condition if" (solution donnée)
- "Voici le code corrigé: ..." (correction automatique)

Tu es là pour aider l'étudiant à PENSER, pas pour penser à sa place."""

    def __init__(self, model: str = "llama3.1:latest"):
        """Initialize the Socratic Duck.

        Args:
            model: The Ollama model to use
        """
        self.bridge = OllamaBridge(model=model)
        self.conversation_history: List[Dict[str, str]] = []

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []

    def ask(self, student_message: str) -> Optional[str]:
        """Process a student message and return a Socratic question.

        Args:
            student_message: What the student said/asked

        Returns:
            A Socratic question to help the student think
        """
        # Build context from history
        context_parts = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                context_parts.append(f"Etudiant: {msg['content']}")
            elif msg["role"] == "assistant":
                context_parts.append(f"Canard: {msg['content']}")

        context = "\n".join(context_parts[-6:])  # Last 3 exchanges

        # Build prompt
        if context:
            prompt = f"{context}\nEtudiant: {student_message}\nCanard:"
        else:
            prompt = f"Etudiant: {student_message}\nCanard:"

        # Get response using generate (simpler than chat)
        response = self.bridge.generate(
            prompt=prompt,
            system=self.SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=200
        )

        if response:
            # Clean up response
            response = response.strip()
            # Remove any "Canard:" prefix if present
            if response.lower().startswith("canard:"):
                response = response[7:].strip()

            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": student_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response

        return None

    def get_conversation_log(self) -> List[Dict[str, str]]:
        """Get the full conversation history for documentation.

        Returns:
            List of messages (excluding system prompt)
        """
        return [msg for msg in self.conversation_history if msg["role"] != "system"]


class ValidateurOllama:
    """Objective validator that audits Kiro's work using Ollama.

    This validator is INDEPENDENT from Kiro (Claude) because:
    - Different model (llama3.1 vs Claude)
    - Local execution (no shared API)
    - Cannot be influenced by Kiro

    Used in "Kiro va à l'école" architecture where:
    - Kiro (Claude) = Student doing the work
    - ValidateurOllama (llama3.1) = Objective examiner
    """

    SYSTEM_PROMPT = """Tu es un correcteur d'examen rigoureux et objectif pour un cours de programmation.

Tu recois trois versions d'un code:
1. CODE ORIGINAL: Le code avec un bug que l'etudiant devait corriger
2. CODE SOUMIS: Le travail de l'etudiant (sa tentative de correction)
3. CODE REFERENCE: La solution correcte de reference

Tu dois evaluer objectivement si l'etudiant a:
- Soumis du code Python syntaxiquement valide (pas d'erreurs SyntaxError)
- Vraiment corrige le bug (pas juste cache ou contourne)
- Fait un travail original (pas copie la reference mot pour mot)
- Compris le probleme (la correction montre une comprehension)

VERIFICATION SYNTAXE (CRITIQUE):
- Verifie que le code soumis peut etre parse sans erreur
- Cherche: parentheses manquantes, crochets ouverts [], indentation incorrecte
- Si le code a une SyntaxError, syntaxe_valide=false et verdict=REJETE

BAREME DE NOTATION (utilise toute l'echelle):
- 95-100: Excellent - Bug corrige + solution elegante + code exemplaire
- 85-94:  Tres bien - Bug corrige proprement, bonne comprehension
- 75-84:  Bien - Bug corrige, solution correcte mais standard
- 65-74:  Assez bien - Bug corrige mais solution sous-optimale
- 50-64:  Passable - Bug partiellement corrige ou solution fragile
- 25-49:  Insuffisant - Tentative visible mais echec
- 0-24:   Echec - Pas de correction ou code casse OU syntaxe invalide

IMPORTANT: Sois strict mais juste. Utilise vraiment les differents paliers selon la qualite du travail.

Reponds UNIQUEMENT en JSON valide avec cette structure exacte:
{
    "verdict": "VALIDE" ou "REJETE",
    "syntaxe_valide": true ou false,
    "bug_corrige": true ou false,
    "copie_detectee": true ou false,
    "comprehension_score": 0 a 100,
    "explication": "MINIMUM 3 PHRASES: 1) Ce que l'etudiant a change dans le code. 2) Pourquoi c'est une bonne ou mauvaise correction. 3) Justification du score attribue."
}"""

    def __init__(self, model: str = "llama3.1:latest", log_dir: str = "/mnt/d/kiro/logs/ollama_audit"):
        """Initialize the validator.

        Args:
            model: The Ollama model to use for validation
            log_dir: Directory for audit logs
        """
        self.bridge = OllamaBridge(model=model)
        self.model = model
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_trail = []

        # Setup file handler for this session
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.audit_file = self.log_dir / f"audit_{session_id}.log"

        # Configure logger with file handler
        file_handler = logging.FileHandler(self.audit_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        logger.addHandler(file_handler)
        logger.info(f"=== SESSION AUDIT OLLAMA DÉMARRÉE === Modèle: {model}")

    @staticmethod
    def validate_python_syntax(code: str) -> Dict[str, Any]:
        """Validate Python code syntax using py_compile.

        This is a fast, deterministic check that catches SyntaxError before
        sending code to Ollama for semantic validation.

        Args:
            code: The Python code to validate

        Returns:
            Dictionary with:
            - valid: bool - True if syntax is valid
            - error: str or None - Error message if invalid
            - line: int or None - Line number where error occurred
        """
        import py_compile
        import tempfile
        import os

        result = {"valid": True, "error": None, "line": None}

        # Write code to temp file for py_compile
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py',
                                              delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            # Attempt to compile
            py_compile.compile(temp_path, doraise=True)

        except py_compile.PyCompileError as e:
            result["valid"] = False
            result["error"] = str(e)
            # Extract line number from error message
            import re
            line_match = re.search(r'line (\d+)', str(e))
            if line_match:
                result["line"] = int(line_match.group(1))
            logger.warning(f"[SYNTAX CHECK] Code invalide: {e}")

        except SyntaxError as e:
            result["valid"] = False
            result["error"] = f"{e.msg} at line {e.lineno}"
            result["line"] = e.lineno
            logger.warning(f"[SYNTAX CHECK] SyntaxError: {e}")

        except Exception as e:
            # Non-syntax error (file issue, etc.) - assume valid
            logger.warning(f"[SYNTAX CHECK] Exception inattendue: {e}")

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

        if result["valid"]:
            logger.info("[SYNTAX CHECK] Code Python valide")
        else:
            logger.info(f"[SYNTAX CHECK] ÉCHEC - Ligne {result['line']}: {result['error']}")

        return result

    def ensure_model_loaded(self) -> bool:
        """Charge le modèle en VRAM si nécessaire (warm-up).

        Le premier appel à Ollama après inactivité peut être de moindre qualité
        car le modèle (~5.5 GB pour llama3.1) doit être chargé en VRAM.
        Cette fonction fait un appel "ping" léger pour pré-charger le modèle.

        Returns:
            True si un warm-up a été effectué, False si le modèle était déjà chargé
        """
        if not GPU_MONITOR_AVAILABLE:
            # Sans monitoring GPU, on fait quand même un warm-up par sécurité
            logger.info("[WARM-UP] GPU monitor non disponible, warm-up préventif...")
            self.bridge.generate("OK", temperature=0.0, max_tokens=5)
            return True

        stats = get_gpu_stats()
        if stats is None:
            logger.warning("[WARM-UP] Impossible de lire les stats GPU")
            return False

        vram_percent = stats['percent']

        # Si VRAM < 50%, le modèle n'est probablement pas chargé
        if vram_percent < 50:
            logger.info(f"[WARM-UP] VRAM à {vram_percent}% - Modèle non chargé, chargement...")
            self.bridge.generate("OK", temperature=0.0, max_tokens=5)

            # Vérifier que le modèle est bien chargé
            stats_after = get_gpu_stats()
            if stats_after:
                logger.info(f"[WARM-UP] Modèle chargé! VRAM: {stats_after['percent']}%")
            return True
        else:
            logger.info(f"[WARM-UP] VRAM à {vram_percent}% - Modèle déjà chargé, skip warm-up")
            return False

    def valider_travail(
        self,
        code_original: str,
        code_soumis: str,
        code_reference: str,
        enonce: str = ""
    ) -> Dict[str, Any]:
        """Validate student work by comparing original, submitted, and reference code.

        Args:
            code_original: The original buggy code (exercice.py)
            code_soumis: The student's submitted correction
            code_reference: The reference solution (corrige.py)
            enonce: Optional lesson description for context

        Returns:
            Dictionary with verdict and analysis:
            {
                "verdict": "VALIDE" or "REJETE",
                "bug_corrige": bool,
                "copie_detectee": bool,
                "comprehension_score": int (0-100),
                "explication": str,
                "raw_response": str (for debugging)
            }
        """
        # === WARM-UP: S'assurer que le modèle est chargé en VRAM ===
        self.ensure_model_loaded()

        # === OPTION E: Pré-vérification syntaxique avec py_compile ===
        syntax_check = self.validate_python_syntax(code_soumis)
        syntax_precheck = {
            "py_compile_valid": syntax_check["valid"],
            "py_compile_error": syntax_check["error"],
            "py_compile_line": syntax_check["line"]
        }

        # Build the prompt with all three code versions
        # Limite augmentée à 10000 chars (2026-01-12) - llama3.1 supporte 128K tokens
        prompt = f"""Voici le travail a evaluer:

=== CODE ORIGINAL (avec bug) ===
{code_original[:10000]}

=== CODE SOUMIS PAR L'ETUDIANT ===
{code_soumis[:10000]}

=== CODE DE REFERENCE (solution) ===
{code_reference[:10000]}

{f"=== ENONCE ==={chr(10)}{enonce[:500]}" if enonce else ""}

Analyse ce travail et donne ton verdict.

IMPORTANT: Reponds UNIQUEMENT avec un objet JSON valide, sans texte avant ou apres. Format exact:
{{"verdict": "VALIDE", "bug_corrige": true, "copie_detectee": false, "comprehension_score": 75, "explication": "..."}}"""

        # === AUDIT LOG: Avant l'appel Ollama ===
        call_timestamp = datetime.now().isoformat()
        logger.info(f"[APPEL OLLAMA] Timestamp: {call_timestamp}")
        logger.info(f"[APPEL OLLAMA] Modèle: {self.model}")
        logger.debug(f"[PROMPT ENVOYÉ]\n{prompt[:1000]}...")
        logger.debug(f"[SYSTEM PROMPT]\n{self.SYSTEM_PROMPT[:500]}...")

        # === GPU MONITOR: Vérification avant appel ===
        gpu_before = None
        gpu_after = None
        if GPU_MONITOR_AVAILABLE:
            gpu_before = get_gpu_stats()
            is_safe, gpu_msg = check_vram_safe(threshold=85)
            log_gpu_status("AVANT Ollama")
            if not is_safe:
                logger.warning(f"[GPU WARNING] {gpu_msg}")

        # Get validation from Ollama (paramètres déterministes)
        response = self.bridge.generate(
            prompt=prompt,
            system=self.SYSTEM_PROMPT,
            temperature=0.0,  # Greedy decoding - most deterministic
            max_tokens=500,
            seed=42,          # Fixed seed for reproducibility
            top_k=1           # Only consider top token - fully deterministic
        )

        # === GPU MONITOR: Vérification après appel ===
        if GPU_MONITOR_AVAILABLE:
            gpu_after = get_gpu_stats()
            log_gpu_status("APRÈS Ollama")

        # === AUDIT LOG: Après l'appel Ollama ===
        logger.info(f"[RÉPONSE OLLAMA] Reçue: {len(response) if response else 0} caractères")
        logger.debug(f"[RÉPONSE BRUTE]\n{response}")

        # Parse the response
        result = {
            "verdict": "ERREUR",
            "syntaxe_valide": None,  # None = non vérifié, True/False = vérifié par Ollama
            "bug_corrige": False,
            "copie_detectee": False,
            "comprehension_score": 0,
            "explication": "Impossible d'obtenir une reponse du validateur",
            "raw_response": response
        }

        if response:
            try:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    result.update({
                        "verdict": parsed.get("verdict", "ERREUR"),
                        "syntaxe_valide": parsed.get("syntaxe_valide", None),
                        "bug_corrige": parsed.get("bug_corrige", False),
                        "copie_detectee": parsed.get("copie_detectee", False),
                        "comprehension_score": parsed.get("comprehension_score", 0),
                        "explication": parsed.get("explication", "Pas d'explication"),
                        "raw_response": response
                    })
            except json.JSONDecodeError:
                result["explication"] = f"Reponse non-JSON: {response[:200]}"
                logger.error(f"[ERREUR PARSING] JSON invalide: {response[:200]}")

        # === AUDIT LOG: Verdict final ===
        logger.info(f"[VERDICT] {result['verdict']} | Score: {result['comprehension_score']}/100")
        logger.info(f"[VERDICT] Bug corrigé: {result['bug_corrige']} | Copie: {result['copie_detectee']}")
        logger.info(f"[VERDICT] Explication: {result['explication']}")
        logger.info(f"[AUDIT] Fichier log: {self.audit_file}")

        # === GPU METRICS: Ajouter au résultat ===
        if gpu_before and gpu_after:
            result["gpu_metrics"] = {
                "vram_before_mb": gpu_before.get("used_mb", 0),
                "vram_after_mb": gpu_after.get("used_mb", 0),
                "vram_total_mb": gpu_before.get("total_mb", 0),
                "vram_delta_mb": gpu_after.get("used_mb", 0) - gpu_before.get("used_mb", 0),
                "gpu_util_before": gpu_before.get("gpu_util", 0),
                "gpu_util_after": gpu_after.get("gpu_util", 0)
            }
            logger.info(f"[GPU METRICS] VRAM: {gpu_before.get('used_mb')} -> {gpu_after.get('used_mb')} MB")

        # === SYNTAX PRECHECK: Ajouter la vérification py_compile au résultat ===
        result["syntax_precheck"] = syntax_precheck

        # Vérification de cohérence: si py_compile dit invalide mais Ollama dit valide, on corrige
        if not syntax_precheck["py_compile_valid"]:
            if result["verdict"] == "VALIDE":
                logger.warning("[INCOHÉRENCE] py_compile=INVALIDE mais Ollama=VALIDE - Correction automatique!")
                result["verdict"] = "REJETE"
                result["syntaxe_valide"] = False
                result["comprehension_score"] = min(result["comprehension_score"], 24)
                result["explication"] = f"[REJET AUTO - SyntaxError détectée ligne {syntax_precheck['py_compile_line']}] " + result["explication"]

        # Save to audit trail
        self.audit_trail.append({
            "timestamp": call_timestamp,
            "model": self.model,
            "result": result
        })

        return result

    def valider_lesson(self, lesson_path: str, code_soumis: str) -> Dict[str, Any]:
        """Validate work for a specific lesson by loading files automatically.

        Args:
            lesson_path: Path to lesson directory (e.g., /mnt/d/kiro/kiro_lessons/lesson-001)
            code_soumis: The student's submitted code

        Returns:
            Validation result dictionary
        """
        from pathlib import Path

        lesson_dir = Path(lesson_path)

        # Load original (exercice.py)
        exercice_path = lesson_dir / "exercice.py"
        if not exercice_path.exists():
            return {"verdict": "ERREUR", "explication": f"exercice.py non trouve dans {lesson_path}"}
        code_original = exercice_path.read_text(encoding='utf-8')

        # Load reference (corrige.py)
        corrige_path = lesson_dir / "corrige.py"
        if not corrige_path.exists():
            return {"verdict": "ERREUR", "explication": f"corrige.py non trouve dans {lesson_path}"}
        code_reference = corrige_path.read_text(encoding='utf-8')

        # Load enonce (README)
        enonce = ""
        for readme in lesson_dir.glob("README*.md"):
            enonce = readme.read_text(encoding='utf-8')[:1000]
            break

        return self.valider_travail(
            code_original=code_original,
            code_soumis=code_soumis,
            code_reference=code_reference,
            enonce=enonce
        )


# CLI interface for testing
if __name__ == "__main__":
    print("=== Test Ollama Bridge ===\n")

    bridge = OllamaBridge()

    # Test availability
    print("Checking Ollama availability...")
    if bridge.is_available():
        print("Ollama is available!\n")

        # List models
        print("Available models:")
        for model in bridge.list_models():
            print(f"  - {model['name']} ({model['size_gb']} GB)")

        # Test Canard Socratique
        print("\n=== Test Canard Socratique ===\n")
        canard = CanardSocratique()

        test_messages = [
            "Mon code Python ne marche pas",
            "J'ai une erreur NameError",
            "La variable n'est pas définie"
        ]

        for msg in test_messages:
            print(f"Étudiant: {msg}")
            response = canard.ask(msg)
            print(f"Canard: {response}\n")
    else:
        print("Ollama is not available. Make sure it's running on Windows.")
