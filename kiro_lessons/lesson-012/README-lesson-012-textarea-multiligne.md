# Cours 012: CSS Input - Textarea Multi-ligne

## Niveau: Debutant

## Duree estimee: 15-20 minutes

## Prerequis

- Bases de HTML
- Bases de CSS
- Comprendre les formulaires

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur un chat AI. L'utilisateur veut poser des questions complexes, mais l'input est limite a une seule ligne.

### Code problematique

```html
<div class="chat-input">
    <input type="text" placeholder="Type your message...">
    <button>Send</button>
</div>
```

### Les problemes

1. **Une seule ligne**: Impossible de voir une longue question
2. **Pas de retour a la ligne**: L'utilisateur ne peut pas formater
3. **Overflow cache**: Le texte long disparait a gauche
4. **UX frustrante**: Copier-coller de code impossible

### Exemple de frustration

```
Input single-line:
┌────────────────────────────────────────────────┐
│ ...vectors, and how do I implement hybrid sea │  <- texte tronque!
└────────────────────────────────────────────────┘

Ce que l'utilisateur voulait ecrire:
"Can you explain RAG architecture, including
embeddings, vector databases, and how do I
implement hybrid search with reranking?"
```

---

## Partie 2: Ta Mission

### Objectif

Remplacer l'input single-line par un textarea multi-ligne.

### Specifications

| Propriete | Valeur |
|-----------|--------|
| Lignes par defaut | 3 |
| Hauteur min | 60px |
| Hauteur max | 150px |
| Redimensionnement | Vertical seulement |

---

## Partie 3: Exercice Pratique

### Etape 1: Comprendre le probleme

```bash
python exercice.py
```

### Etape 2: Implementer la solution

1. Remplacer `<input>` par `<textarea>`
2. Ajouter le CSS approprié
3. Gerer l'envoi avec Enter (+ Shift+Enter pour nouvelle ligne)

---

## Partie 4: Corrige (Solution Complete)

### HTML corrige

```html
<div class="chat-input-container">
    <div class="input-wrapper">
        <textarea
            class="chat-textarea"
            rows="3"
            placeholder="Type your message... (Shift+Enter for new line)"
        ></textarea>
        <button class="send-button">Send</button>
    </div>
</div>
```

### CSS corrige

```css
.chat-input-container {
    padding: 10px;
    background: #1a1a2e;
    border-top: 1px solid #00ff41;
}

.input-wrapper {
    display: flex;
    gap: 10px;
    align-items: flex-end;  /* Bouton en bas */
}

.chat-textarea {
    flex: 1;
    min-height: 60px;
    max-height: 150px;
    padding: 10px;
    border: 1px solid #00ff41;
    border-radius: 4px;
    background: #0a0a14;
    color: #00ff41;
    font-family: monospace;
    font-size: 14px;
    resize: vertical;  /* Redimensionnement vertical seulement */
    line-height: 1.4;
}

.chat-textarea:focus {
    outline: none;
    border-color: #00ff88;
    box-shadow: 0 0 5px rgba(0, 255, 65, 0.3);
}

.chat-textarea::placeholder {
    color: #00ff4180;
}

.send-button {
    padding: 10px 20px;
    height: 40px;
    background: #00ff41;
    color: #0a0a14;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}
```

### JavaScript pour Enter/Shift+Enter

```javascript
const textarea = document.querySelector('.chat-textarea');

textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();  // Empeche le retour a la ligne
        sendMessage();       // Envoie le message
    }
    // Shift+Enter = nouvelle ligne (comportement par defaut)
});
```

---

## Partie 5: Lecons Apprises

### 1. Input vs Textarea

```html
<!-- Input: une seule ligne -->
<input type="text">

<!-- Textarea: plusieurs lignes -->
<textarea rows="3"></textarea>
```

### 2. Controler le redimensionnement

```css
/* Pas de redimensionnement */
textarea { resize: none; }

/* Vertical seulement */
textarea { resize: vertical; }

/* Horizontal seulement */
textarea { resize: horizontal; }

/* Les deux (defaut) */
textarea { resize: both; }
```

### 3. Hauteur min/max

```css
textarea {
    min-height: 60px;   /* Au moins 3 lignes */
    max-height: 150px;  /* Pas plus de ~7 lignes */
}
```

### 4. Alignement du bouton

```css
.input-wrapper {
    display: flex;
    align-items: flex-end;  /* Bouton aligne en bas */
}
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Quelle est la difference entre `<input type="text">` et `<textarea>`?

<details>
<summary>Reponse</summary>
- `<input type="text">`: Une seule ligne, pas de retour a la ligne
- `<textarea>`: Plusieurs lignes, supporte les retours a la ligne

Textarea est ideal pour les textes longs (messages, commentaires, code).
</details>

### Question 2
Comment empecher le redimensionnement horizontal d'un textarea?

<details>
<summary>Reponse</summary>

```css
textarea {
    resize: vertical;
}
```

Cela permet le redimensionnement vertical seulement, gardant la largeur fixe.
</details>

### Question 3
Comment envoyer avec Enter mais permettre Shift+Enter pour nouvelle ligne?

<details>
<summary>Reponse</summary>

```javascript
textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
```

- Enter seul: envoie le message
- Shift+Enter: nouvelle ligne (comportement par defaut)
</details>

---

## Partie 7: Patterns de Textarea

### Pattern: Auto-resize

```javascript
const textarea = document.querySelector('textarea');

textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
});
```

### Pattern: Character counter

```html
<div class="textarea-wrapper">
    <textarea maxlength="500"></textarea>
    <span class="char-count">0/500</span>
</div>
```

```javascript
textarea.addEventListener('input', () => {
    charCount.textContent = `${textarea.value.length}/500`;
});
```

---

## Ressources Supplementaires

- [MDN: textarea](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea)
- [CSS resize property](https://developer.mozilla.org/en-US/docs/Web/CSS/resize)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
