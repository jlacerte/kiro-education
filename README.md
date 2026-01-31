# Kiro Educational System V3.2

Systeme d'apprentissage intelligent pour la programmation Python avec validation automatique et suivi Archon.

## Fonctionnalites

- **Dual Engine**: Support Kiro CLI et Claude CLI avec la meme infrastructure
- **Validation Ministerielle**: 5 verrous de controle qualite
- **Archon Integration**: Suivi de projets et taches en temps reel
- **Ollama Validation**: Validation locale GPU avec llama3.1
- **AST Analysis**: Detection de bugs par analyse syntaxique avancee

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer une lecon avec Kiro
```bash
python cli/kiro_education.py go "lesson-001" --engine kiro
```

### Lancer une lecon avec Claude
```bash
python cli/kiro_education.py go "lesson-001" --engine claude
```

### Changer de serveur Archon
```bash
ARCHON_URL=https://mon-archon.com python cli/kiro_education.py go "lesson-001"
```

## Lecons disponibles

| Lecon | Type | Description |
|-------|------|-------------|
| lesson-001 | debugging | Bug silencieux - Variable non initialisee |
| lesson-002 | security | Tokens hardcodes et fallbacks dangereux |
| lesson-003 | exercise | Exercice pratique |

## Architecture

```
kiro-education/
├── cli/                    # Interface CLI (Typer)
├── core/                   # Orchestrateur, grading, validation
├── executor/               # Execution Kiro/Claude
├── archon/                 # Client HTTP Archon
├── models/                 # Modeles Pydantic
├── config/                 # Configuration centralisee
├── kiro_lessons/           # Exercices Python
└── logs/                   # Logs de session
```

## Configuration

Editez `config/archon_config.py` ou utilisez les variables d'environnement:

| Variable | Default | Description |
|----------|---------|-------------|
| ARCHON_URL | https://archon.nxtcloud.ca | URL du serveur Archon |
| ARCHON_TIMEOUT | 30.0 | Timeout HTTP (secondes) |

## Hackathon Dynamous Kiro 2026

Projet developpe pour le hackathon avec focus sur:
- Comparaison equitable Kiro vs Claude
- Infrastructure de logging transparente
- Validation automatique des corrections
