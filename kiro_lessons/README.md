# Kiro Academy - Lessons

> Cours pratiques de programmation Python bases sur des bugs reels

---

## Lessons Disponibles

| # | Titre | Niveau | Duree |
|---|-------|--------|-------|
| 001 | [Bug Silencieux - Variable Non Initialisee](lesson-001/) | Debutant | 30-45 min |
| 002 | [Securite - Tokens Hardcodes](lesson-002/) | Debutant | 30-45 min |
| 003 | [Clean Code - Imports Dupliques](lesson-003/) | Debutant | 15-20 min |
| 004 | [Securite Web - XSS via innerHTML](lesson-004/) | Intermediaire | 45-60 min |
| 005 | [Clean Code - Code Mort](lesson-005/) | Debutant | 15-20 min |
| 006 | [Clean Code - Duplication Fichiers](lesson-006/) | Debutant | 20-30 min |
| 007 | [Tests - Token Invalide](lesson-007/) | Intermediaire | 25-35 min |
| 008 | [Routes Admin Manquantes](lesson-008/) | Intermediaire | 25-35 min |
| 009 | [Fixation Fonctionnelle](lesson-009/) | Intermediaire | 30-40 min |
| 010 | [Recherche Multi-Sources](lesson-010/) | Intermediaire | 35-45 min |
| 011 | [CSS - Consolidation Status Bars](lesson-011/) | Intermediaire | 25-35 min |
| 012 | [CSS - Textarea Multi-ligne](lesson-012/) | Debutant | 15-20 min |
| 013 | [CSS - Position Fixed UI](lesson-013/) | Intermediaire | 30-40 min |
| 014 | [Pattern - Workflow Detection](lesson-014/) | Avance | 40-50 min |

---

## Comment Utiliser

### 1. Choisir une lesson

```bash
cd kiro_lessons/lesson-001
```

### 2. Lire le README

```bash
cat README.md
# ou ouvrir dans un editeur
```

### 3. Lancer l'exercice

```bash
python exercice.py
```

### 4. Corriger le bug

Edite `exercice.py` jusqu'a ce que tous les tests passent.

### 5. Comparer avec le corrige

```bash
python corrige.py
diff exercice.py corrige.py
```

---

## Structure d'une Lesson

```
lesson-XXX/
├── __init__.py                    # Metadata de la lesson
├── README-{concept}.md            # Enonce complet du cours
├── exercice.py                    # Code buggy a corriger
└── corrige.py                     # Solution avec explications
```

---

## Contribuer

Les lessons sont basees sur des bugs reels trouves dans le projet Blade Runner.
Voir le dossier `.issues/` pour les issues originales.

---

*Kiro Academy - Apprendre en corrigeant des vrais bugs*
