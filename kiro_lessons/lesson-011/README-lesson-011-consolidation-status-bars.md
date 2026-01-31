# Cours 011: CSS Layout - Consolidation des Status Bars

## Niveau: Intermediaire

## Duree estimee: 25-35 minutes

## Prerequis

- Bases de HTML/CSS
- Comprendre le box model
- Notions de layout Flexbox

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur une application avec une interface style terminal. En bas de l'ecran, il y a **3 barres de status differentes** qui affichent des informations redondantes.

### Layout actuel (problematique)

```
┌────────────────────────────────────────────────────────────────┐
│  Header                                                        │
├────────────┬───────────────────────────────────────────────────┤
│            │                                                   │
│  Sidebar   │         Zone de contenu                          │
│            │                                                   │
│            ├───────────────────────────────────────────────────┤
│            │  ● Connected | 1 artifact | 4 videos | 01:32     │ ← Status 1
├────────────┴───────────────────────────────────────────────────┤
│  F1 Help | F2 Menu | F3 View | F4 Edit | ... | F10 Quit        │ ← Status 2
├────────────────────────────────────────────────────────────────┤
│  SYSTEM: ONLINE | MEMORY: N/A | UPTIME: N/A                    │ ← Status 3
└────────────────────────────────────────────────────────────────┘
   SOUND: OFF (flottant)                                          ← Status 4!
```

### Les problemes

1. **Redondance**: 3-4 barres de status avec infos qui se chevauchent
2. **Espace perdu**: ~100px de hauteur pour des status bars
3. **Confusion**: Ou regarder pour quelle info?
4. **F-keys inutiles**: La barre F1-F10 n'est jamais utilisee

---

## Partie 2: Ta Mission

### Objectif

Consolider toutes les informations de status en **une seule ligne** bien organisee.

### Separation des responsabilites

| Zone | Type d'info | Exemples |
|------|-------------|----------|
| Sidebar | Stats CONTENU | Videos, Artifacts, Channels |
| Status Line | Stats SYSTEME | Connexion, Memoire, Uptime, Son |

### Layout propose

```
┌────────────────────────────────────────────────────────────────┐
│  Header                                                        │
├────────────┬───────────────────────────────────────────────────┤
│            │                                                   │
│  Sidebar   │         Zone de contenu                          │
│  ────────  │         (plus d'espace!)                         │
│  4 Videos  │                                                   │
│  1 Channel │                                                   │
│            │                                                   │
├────────────┴───────────────────────────────────────────────────┤
│  ● SYSTEM: ONLINE | MEM: 38% | UPTIME: 2h | 14:32 | SOUND: OFF │ ← Status unique
└────────────────────────────────────────────────────────────────┘
```

---

## Partie 3: Exercice Pratique

### Etape 1: Identifier les informations

```bash
python exercice.py
```

### Etape 2: Categoriser

- Quelles infos sont **systeme**? (connexion, memoire, temps)
- Quelles infos sont **contenu**? (videos, artifacts)
- Quelles infos sont **inutiles**? (F-keys jamais utilisees)

### Etape 3: Consolider

Une seule status line avec toutes les infos systeme importantes.

---

## Partie 4: Corrige (Solution Complete)

### CSS pour cacher les barres redondantes

```css
/* Cacher la barre F-keys (jamais utilisee) */
.function-keys-bar {
    display: none !important;
}

/* Cacher le footer redondant en mode dual-pane */
.dual-pane-layout:has(.mc-status-bar) .footer {
    display: none !important;
}

/* Cacher l'indicateur SOUND flottant (integre dans status line) */
.sound-indicator-float {
    display: none !important;
}
```

### HTML de la Status Line unique

```html
<div class="mc-status-bar">
    <span class="status-dot online"></span>
    <span class="status-item">SYSTEM: ONLINE</span>
    <span class="status-separator">|</span>
    <span class="status-item">MEM: <span id="memory-usage">38%</span></span>
    <span class="status-separator">|</span>
    <span class="status-item">UPTIME: <span id="uptime">2h</span></span>
    <span class="status-separator">|</span>
    <span class="status-item" id="clock">14:32</span>
    <span class="status-separator">|</span>
    <span class="status-item clickable" id="sound-toggle">SOUND: OFF</span>
</div>
```

### CSS de la Status Line

```css
.mc-status-bar {
    height: 28px;
    background: linear-gradient(to bottom, #1a1a2e, #0f0f1a);
    border-top: 1px solid #00ff41;
    color: #00ff41;
    font-family: monospace;
    font-size: 12px;
    display: flex;
    align-items: center;
    padding: 0 15px;
    gap: 8px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00ff41;
}

.status-dot.online {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.status-separator {
    color: #00ff4180;
}

.status-item.clickable {
    cursor: pointer;
}

.status-item.clickable:hover {
    text-decoration: underline;
}
```

---

## Partie 5: Lecons Apprises

### 1. Moins c'est plus

```css
/* MAUVAIS - 3 barres de status */
.status-bar-1 { height: 30px; }
.status-bar-2 { height: 30px; }
.status-bar-3 { height: 30px; }
/* Total: 90px perdus */

/* BON - 1 seule barre */
.mc-status-bar { height: 28px; }
/* Gain: 62px d'espace vertical */
```

### 2. Separation des responsabilites

```
CONTENU (sidebar):        SYSTEME (status line):
- Nombre de videos       - Etat connexion
- Nombre d'artifacts     - Utilisation memoire
- Channels suivis        - Uptime
                         - Horloge
                         - Parametres (son)
```

### 3. Supprimer l'inutile

```css
/* Si personne n'utilise F1-F10, supprimez-le */
.function-keys-bar {
    display: none;
}

/* Pas de culpabilite! */
```

### 4. Animation subtile pour le status

```css
/* Un petit pulse pour montrer "je suis vivant" */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi avoir 3 status bars est problematique?

<details>
<summary>Reponse</summary>
- Gaspillage d'espace vertical (~90px)
- Confusion: ou regarder?
- Redondance: memes infos a plusieurs endroits
- Charge cognitive: trop d'elements a parser
</details>

### Question 2
Comment decider quoi mettre dans la sidebar vs la status line?

<details>
<summary>Reponse</summary>
- **Sidebar**: Stats liees au CONTENU (ce que l'utilisateur a cree/importe)
- **Status Line**: Stats SYSTEME (etat de l'application elle-meme)

La sidebar repond a "Qu'est-ce que j'ai?"
La status line repond a "Comment va l'app?"
</details>

### Question 3
Pourquoi utiliser `display: none` plutot que supprimer le HTML?

<details>
<summary>Reponse</summary>
- Garde le HTML intact (peut etre reactive plus tard)
- Plus facile a tester (toggle via DevTools)
- Pas de risque de casser du JavaScript qui reference l'element
- Possibilite d'ajouter un toggle utilisateur plus tard
</details>

---

## Partie 7: Patterns de Status Bar

### Pattern: Status Line avec sections

```css
.status-bar {
    display: flex;
    justify-content: space-between;
}

.status-left { /* Infos systeme */ }
.status-center { /* Notifications */ }
.status-right { /* Horloge, son */ }
```

### Pattern: Status responsive

```css
/* Mobile: icones seulement */
@media (max-width: 768px) {
    .status-item span.label { display: none; }
}

/* Desktop: texte complet */
@media (min-width: 769px) {
    .status-item span.label { display: inline; }
}
```

---

## Ressources Supplementaires

- [CSS Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [Status Bar Design Patterns](https://www.nngroup.com/articles/status-bars/)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
