"""
Générateur de titres descriptifs pour les projets Archon basé sur l'analyse du code étudiant.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class DescriptiveTitleGenerator:
    """Génère des titres descriptifs basés sur l'analyse du code étudiant."""
    
    def __init__(self):
        # Mapping des types de problèmes détectés vers des titres descriptifs
        self.issue_titles = {
            "variable_not_initialized": "Variable Non Initialisée",
            "security_vulnerability": "Vulnérabilité Sécurité",
            "syntax_error": "Erreur de Syntaxe", 
            "import_missing": "Import Manquant",
            "logic_error": "Erreur de Logique",
            "exception_handling": "Gestion d'Exceptions",
            "indentation_error": "Erreur d'Indentation",
            "type_error": "Erreur de Type",
            "name_error": "Variable Inconnue",
            "index_error": "Index Hors Limites",
            "key_error": "Clé Manquante",
            "file_not_found": "Fichier Introuvable",
            "division_by_zero": "Division par Zéro",
            "infinite_loop": "Boucle Infinie",
            "memory_leak": "Fuite Mémoire",
            "performance_issue": "Problème Performance"
        }
        
        # Patterns de détection dans le code
        self.detection_patterns = {
            "variable_not_initialized": [
                r"print\(\s*\w+\s*\)",  # print(variable) sans initialisation
                r"return\s+\w+\s*$",    # return variable sans initialisation
                r"\w+\s*\+=\s*\d+",     # variable += sans initialisation
                r"NameError.*not defined",  # erreur variable non définie
            ],
            "security_vulnerability": [
                r"password\s*=\s*['\"][^'\"]*['\"]",  # mot de passe en dur
                r"api_key\s*=\s*['\"][^'\"]*['\"]",   # clé API en dur
                r"token\s*=\s*['\"][^'\"]*['\"]",     # token en dur
                r"VULNERABILITE",                     # commentaire vulnérabilité
                r"Tokens Hardcodes",                  # titre sécurité
                r"FAILLES DE SECURITE",               # commentaire sécurité
                r"eval\s*\(",                         # utilisation d'eval
                r"exec\s*\(",                         # utilisation d'exec
            ],
            "syntax_error": [
                r"print\s+\w+",         # print sans parenthèses (Python 2 style)
                r":\s*$\n\s*\n",        # deux-points suivi de ligne vide
                r"\(\s*\)",             # parenthèses vides mal placées
            ],
            "import_missing": [
                r"import\s+(\w+)",      # import simple
                r"from\s+(\w+)\s+import", # from import
            ],
            "logic_error": [
                r"if\s+\w+\s*=\s*\w+",  # = au lieu de == dans if
                r"while\s+True\s*:",     # boucle infinie potentielle
                r"range\(\s*0\s*\)",     # range(0) inutile
            ]
        }
    
    def analyze_code(self, code_content: str) -> List[str]:
        """Analyser le code pour détecter les types de problèmes."""
        detected_issues = []
        
        for issue_type, patterns in self.detection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code_content, re.MULTILINE | re.IGNORECASE):
                    detected_issues.append(issue_type)
                    break  # Un pattern suffit pour détecter le problème
        
        return detected_issues
    
    def parse_readme_title(self, lesson_path: str) -> Optional[str]:
        """Parser le titre depuis le fichier README descriptif standardisé."""
        try:
            lesson_dir = Path(lesson_path).parent
            
            # Chercher les fichiers README-*.md
            readme_files = list(lesson_dir.glob("README-*.md"))
            
            if not readme_files:
                return None
                
            # Prendre le premier README descriptif trouvé
            readme_file = readme_files[0]
            filename = readme_file.stem  # README-lesson-004-securite-web-xss-innerhtml ou README-bug-silencieux-variable-non-initialisee
            
            # Extraire la partie après "README-"
            if not filename.startswith("README-"):
                return None
                
            title_part = filename[7:]  # lesson-004-securite-web-xss-innerhtml ou bug-silencieux-variable-non-initialisee
            
            # Nouveau format : README-lesson-XXX-titre
            if title_part.startswith("lesson-"):
                # Trouver la partie après lesson-XXX-
                parts = title_part.split("-", 2)  # ["lesson", "004", "securite-web-xss-innerhtml"]
                if len(parts) >= 3:
                    title_part = parts[2]  # securite-web-xss-innerhtml
                else:
                    # Format invalide, utiliser tel quel
                    pass
            
            # Convertir kebab-case vers Title Case
            words = title_part.split("-")
            title_words = []
            
            for word in words:
                # Cas spéciaux pour les acronymes et mots techniques
                if word.upper() in ["XSS", "SQL", "API", "JWT", "HTML", "CSS", "JS"]:
                    title_words.append(word.upper())
                elif word.lower() in ["innerhtml", "javascript"]:
                    title_words.append(word.capitalize())
                else:
                    title_words.append(word.capitalize())
            
            return " ".join(title_words)
            
        except Exception:
            return None

    def generate_title(self, lesson_number: str, lesson_type: str, code_path: str) -> str:
        """Générer un titre descriptif basé sur les README standardisés."""
        try:
            # Priorité 1: Titre depuis README descriptif (nouveau système)
            readme_title = self.parse_readme_title(code_path)
            if readme_title:
                return f"Leçon {lesson_number} - {readme_title}"
            
            # Priorité 2: Analyse de code (fallback existant)
            with open(code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            detected_issues = self.analyze_code(code_content)
            
            if detected_issues:
                primary_issue = detected_issues[0]
                issue_title = self.issue_titles.get(primary_issue, lesson_type.title())
                return f"Leçon {lesson_number} - {issue_title}"
            
            # Priorité 3: Type de leçon générique
            type_mappings = {
                "debugging": "Débogage Python",
                "security": "Sécurité Python", 
                "exercise": "Exercice Python",
                "advanced": "Python Avancé"
            }
            
            mapped_type = type_mappings.get(lesson_type.lower(), lesson_type.title())
            return f"Leçon {lesson_number} - {mapped_type}"
            
        except Exception as e:
            # En cas d'erreur, utiliser un titre générique
            return f"Leçon {lesson_number} - {lesson_type.title()}"
    
    def get_issue_summary(self, code_path: str) -> Dict[str, any]:
        """Obtenir un résumé des problèmes détectés pour les métriques."""
        try:
            with open(code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            detected_issues = self.analyze_code(code_content)
            
            return {
                "issues_detected": len(detected_issues),
                "issue_types": detected_issues,
                "primary_issue": detected_issues[0] if detected_issues else None,
                "code_lines": len(code_content.split('\n'))
            }
        except Exception:
            return {
                "issues_detected": 0,
                "issue_types": [],
                "primary_issue": None,
                "code_lines": 0
            }


def create_descriptive_title_generator() -> DescriptiveTitleGenerator:
    """Factory function pour créer un générateur de titres."""
    return DescriptiveTitleGenerator()
