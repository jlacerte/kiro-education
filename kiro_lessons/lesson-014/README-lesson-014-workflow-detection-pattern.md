# Cours 014: Pattern - Detection de Workflow par Intention

## Niveau: Avance

## Duree estimee: 40-50 minutes

## Prerequis

- Python intermediaire
- Comprendre les patterns de design
- Notions de state machines
- Bases de NLP (optionnel)

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur un chatbot AI qui doit guider l'utilisateur a travers differents processus (workflows) selon ce qu'il veut faire.

### Comportement actuel

```
User: "What videos about RAG?"
AI: "I can help you with that. [reponse generique]"

User: "Show me the artifacts"
AI: "I can help you with that. [meme reponse generique]"
```

### Le probleme

Le chat ne distingue pas les **intentions** de l'utilisateur. Il repond de la meme maniere a toutes les questions.

### Comportement desire

```
User: "What videos about RAG?"
AI: [WF1 - Videos] "I found 3 videos about RAG:
     - RAG Tutorial by Cole Medin [Download]
     - Building RAG Systems [Download]"

User: "Show me the artifacts"
AI: [WF2 - Artifacts] "Here are your artifacts:
     - Summary: RAG Tutorial
     - FAQ: RAG Best Practices"
```

---

## Partie 2: Le Pattern Workflow Detection

### Architecture

```
Message utilisateur
       |
       v
┌─────────────────────┐
│  Detecteur          │  <- Analyse le message
│  d'intention        │
└─────────────────────┘
       |
       v
┌─────────────────────┐
│  Charge le prompt   │  <- Fichier MD correspondant
│  du workflow        │
└─────────────────────┘
       |
       v
┌─────────────────────┐
│  AI genere          │  <- Avec contexte specifique
│  la reponse         │
└─────────────────────┘
       |
       v
┌─────────────────────┐
│  Marqueur WF        │  <- <!-- WF:2 --> ou data-wf="2"
│  dans la reponse    │
└─────────────────────┘
       |
       v
Frontend met a jour le bouton WF actif
```

### Workflows definis

| WF | Nom | Patterns | Action |
|----|-----|----------|--------|
| WF1 | Videos | video, watch, youtube | Recherche et suggestions |
| WF2 | Artifacts | artifact, summary, transcript | Liste des artefacts |
| WF3 | RAG/KB | what did, search, find info | Recherche dans la KB |
| WF4 | Generate | generate, create, make | Generation de contenu |
| WF5 | Export | export, download, share | Export de donnees |

---

## Partie 3: Ta Mission

### Objectif

Implementer un systeme de detection de workflow par patterns.

### Specifications

1. **Detection par keywords**: Analyser le message pour identifier l'intention
2. **Prompts modulaires**: Un fichier MD par workflow
3. **Marqueur dans la reponse**: Indiquer le workflow actif
4. **Frontend reactive**: Mettre a jour l'UI

---

## Partie 4: Corrige (Solution Complete)

### 1. Service de detection (Python)

```python
from typing import Dict, List, Optional
from pathlib import Path

WORKFLOW_PATTERNS: Dict[int, List[str]] = {
    1: ['video', 'videos', 'watch', 'youtube', 'channel'],
    2: ['artifact', 'transcript', 'summary', 'notes', 'document'],
    3: ['what did', 'search kb', 'find info', 'knowledge', 'rag'],
    4: ['generate', 'create', 'make', 'produce'],
    5: ['export', 'download', 'share', 'save'],
}

def detect_workflow(message: str) -> int:
    """Detecte le workflow a partir du message."""
    message_lower = message.lower()

    for wf_num, patterns in WORKFLOW_PATTERNS.items():
        if any(pattern in message_lower for pattern in patterns):
            return wf_num

    return 0  # Pas de workflow specifique

def get_workflow_prompt(wf_num: int) -> Optional[str]:
    """Charge le prompt du workflow depuis le fichier MD."""
    if wf_num == 0:
        return None

    prompt_path = Path(f"config/workflows/wf{wf_num}.md")
    if prompt_path.exists():
        return prompt_path.read_text()

    return None
```

### 2. Fichiers de prompts (Markdown)

**config/workflows/wf1.md**
```markdown
# Workflow 1: Video Discovery

Tu es un assistant qui aide a trouver des videos YouTube.

## Comportement
- Recherche dans l'index video
- Propose des boutons Download pour les videos sans transcript
- Format: liste avec titre, channel, et action

## Format de reponse
Toujours terminer par le marqueur:
<span class="wf-marker" data-wf="1"></span>
```

**config/workflows/wf2.md**
```markdown
# Workflow 2: Artifacts

Tu es un assistant qui gere les artefacts (summaries, FAQs, transcripts).

## Comportement
- Liste les artefacts disponibles
- Permet de visualiser, editer, exporter
- Groupe par type (summary, faq, podcast)

## Format de reponse
<span class="wf-marker" data-wf="2"></span>
```

### 3. Integration dans le chat (Python)

```python
async def process_message(message: str) -> str:
    # 1. Detecter le workflow
    wf_num = detect_workflow(message)

    # 2. Charger le prompt specifique
    wf_prompt = get_workflow_prompt(wf_num)

    # 3. Construire le contexte
    context = build_context(message, wf_num)

    # 4. Generer la reponse avec l'AI
    response = await ai.generate(
        system_prompt=wf_prompt or DEFAULT_PROMPT,
        user_message=message,
        context=context
    )

    # 5. Ajouter le marqueur WF
    if wf_num > 0:
        response += f'\n<span class="wf-marker" data-wf="{wf_num}"></span>'

    return response
```

### 4. Frontend (JavaScript)

```javascript
class WorkflowManager {
    constructor() {
        this.activeWorkflow = 0;
        this.buttons = document.querySelectorAll('.wf-button');
    }

    parseResponse(html) {
        // Chercher le marqueur
        const marker = html.match(/data-wf="(\d)"/);
        if (marker) {
            this.setActive(parseInt(marker[1]));
        }
    }

    setActive(wfNum) {
        this.activeWorkflow = wfNum;

        // Mettre a jour les boutons
        this.buttons.forEach((btn, index) => {
            btn.classList.toggle('active', index + 1 === wfNum);
        });
    }
}

// Utilisation
const wfManager = new WorkflowManager();

// Apres chaque reponse du chat
chatElement.addEventListener('htmx:afterSwap', (e) => {
    wfManager.parseResponse(e.detail.elt.innerHTML);
});
```

---

## Partie 5: Lecons Apprises

### 1. Separation des preoccupations

```
Detection    -> workflow_service.py
Prompts      -> config/workflows/*.md
Generation   -> ai_provider.py
UI           -> blade-runner.js
```

### 2. Prompts modulaires

```
# Avantages des fichiers MD:
- Facile a editer sans toucher au code
- Version control (git diff lisible)
- Non-developpeurs peuvent modifier
- Tests A/B faciles
```

### 3. Marqueurs discrets

```html
<!-- Visible par le JS, invisible pour l'utilisateur -->
<span class="wf-marker" data-wf="2" style="display:none"></span>

<!-- Ou en commentaire HTML -->
<!-- WF:2 -->
```

### 4. Patterns extensibles

```python
# Facile d'ajouter un nouveau workflow
WORKFLOW_PATTERNS[6] = ['settings', 'config', 'preferences']
# + Creer wf6.md
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi utiliser des fichiers MD plutot que du code Python pour les prompts?

<details>
<summary>Reponse</summary>
- Plus facile a editer (pas besoin de savoir coder)
- Meilleur versioning (git diff lisible)
- Separation du code et du contenu
- Possibilite de hot-reload sans redemarrer l'app
- Non-developpeurs peuvent contribuer
</details>

### Question 2
Comment le frontend sait quel workflow est actif?

<details>
<summary>Reponse</summary>
Le backend ajoute un marqueur cache dans la reponse:

```html
<span class="wf-marker" data-wf="2"></span>
```

Le JavaScript parse ce marqueur et met a jour l'UI:

```javascript
const marker = html.match(/data-wf="(\d)"/);
if (marker) {
    this.setActive(parseInt(marker[1]));
}
```
</details>

### Question 3
Que se passe-t-il si aucun pattern ne matche?

<details>
<summary>Reponse</summary>
`detect_workflow()` retourne 0, ce qui signifie:
- Pas de prompt specifique charge
- Utilisation du prompt par defaut
- Pas de marqueur WF ajoute
- Le chat repond de maniere generique
</details>

---

## Partie 7: Patterns Avances

### Pattern: Workflow avec etat

```python
class WorkflowState:
    def __init__(self):
        self.current_wf = 0
        self.history = []
        self.context = {}

    def transition(self, new_wf: int, message: str):
        self.history.append((self.current_wf, message))
        self.current_wf = new_wf

    def can_transition(self, to_wf: int) -> bool:
        # Regles de transition
        valid_transitions = {
            1: [2, 3],  # WF1 peut aller vers WF2 ou WF3
            2: [1, 3],
            3: [1, 2, 4],
        }
        return to_wf in valid_transitions.get(self.current_wf, [])
```

### Pattern: Detection par ML

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class MLWorkflowDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB()

    def train(self, messages: List[str], labels: List[int]):
        X = self.vectorizer.fit_transform(messages)
        self.classifier.fit(X, labels)

    def predict(self, message: str) -> int:
        X = self.vectorizer.transform([message])
        return self.classifier.predict(X)[0]
```

---

## Ressources Supplementaires

- [State Machines in Python](https://python-statemachine.readthedocs.io/)
- [Intent Classification](https://www.tensorflow.org/tutorials/text/text_classification_rnn)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
