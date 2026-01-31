# Cours 013: CSS Position Fixed - Elements UI Persistants

## Niveau: Intermediaire

## Duree estimee: 30-40 minutes

## Prerequis

- Bases de CSS
- Comprendre le positionnement (static, relative, absolute)
- Notions de z-index

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur une application de chat. L'input et la status bar disparaissent quand l'utilisateur scrolle vers le haut pour lire les anciens messages.

### Comportement problematique

```
AVANT SCROLL:
┌────────────────────────────────────────┐
│  Messages...                           │
│  Message 10                            │
│  Message 11                            │
├────────────────────────────────────────┤
│  [Input________________________] Send  │  <- Visible
├────────────────────────────────────────┤
│  ● SYSTEM: ONLINE | 14:32             │  <- Visible
└────────────────────────────────────────┘

APRES SCROLL VERS LE HAUT:
┌────────────────────────────────────────┐
│  Message 1                             │
│  Message 2                             │
│  Message 3                             │
│  Message 4                             │
│  Message 5                             │
│  Message 6                             │
└────────────────────────────────────────┘
  Input et status bar: DISPARUS!
```

### Le probleme

L'utilisateur ne peut plus envoyer de message sans re-scroller vers le bas.

---

## Partie 2: Comprendre Position

### Les 5 valeurs de position

| Position | Comportement |
|----------|-------------|
| `static` | Defaut, suit le flux normal |
| `relative` | Decale par rapport a sa position normale |
| `absolute` | Position par rapport au parent positionne |
| `fixed` | Position par rapport au viewport (ecran) |
| `sticky` | Hybride relative/fixed selon le scroll |

### Fixed vs Absolute

```css
/* Fixed: toujours visible, ignore le scroll */
.element-fixed {
    position: fixed;
    bottom: 0;
    /* Reste en bas de l'ecran peu importe le scroll */
}

/* Absolute: relatif au parent positionne */
.element-absolute {
    position: absolute;
    bottom: 0;
    /* Peut sortir de l'ecran avec le scroll */
}
```

---

## Partie 3: Ta Mission

### Objectif

Faire en sorte que l'input et la status bar restent **toujours visibles** en bas de l'ecran.

### Specifications

| Element | Position | Bottom | Z-index |
|---------|----------|--------|---------|
| Status bar | fixed | 0 | 1000 |
| Input | fixed | 30px | 999 |
| Messages | margin-bottom | 100px | - |

---

## Partie 4: Corrige (Solution Complete)

### CSS pour elements fixes

```css
/* Status bar fixe en bas */
.mc-status-bar {
    position: fixed !important;
    bottom: 0 !important;
    left: 0;
    right: 0;
    height: 28px;
    z-index: 1000;  /* Au-dessus de tout */
    background: #1a1a2e;
    border-top: 1px solid #00ff41;
}

/* Input fixe au-dessus de la status bar */
.chat-input-container {
    position: fixed !important;
    bottom: 30px !important;  /* Hauteur de la status bar + 2px */
    left: 200px !important;   /* Largeur de la sidebar */
    right: 0 !important;
    z-index: 999;
    background: #1a1a2e;
    padding: 10px;
}

/* Espace pour les elements fixes */
.message-area {
    margin-bottom: 100px !important;  /* Input (60px) + Status (28px) + padding */
    overflow-y: auto;
}
```

### Pourquoi !important?

```css
/* Parfois necessaire pour overrider des styles existants */
position: fixed !important;

/* Mais privilegier la specificite CSS quand possible */
.app-container .chat-input-container {
    position: fixed;
}
```

### Gestion de la sidebar

```css
/* L'input doit commencer apres la sidebar */
.chat-input-container {
    left: 200px;  /* Largeur de la sidebar */
}

/* Ou avec calc() pour plus de flexibilite */
.chat-input-container {
    left: var(--sidebar-width, 200px);
}
```

---

## Partie 5: Lecons Apprises

### 1. Fixed pour les elements persistants

```css
/* Elements qui doivent TOUJOURS etre visibles */
.navbar { position: fixed; top: 0; }
.footer { position: fixed; bottom: 0; }
.fab-button { position: fixed; bottom: 20px; right: 20px; }
```

### 2. Z-index pour l'empilement

```css
/* Echelle de z-index coherente */
:root {
    --z-dropdown: 100;
    --z-modal: 200;
    --z-toast: 300;
    --z-fixed-ui: 1000;
}
```

### 3. Espace pour le contenu

```css
/* IMPORTANT: Reserver l'espace pour les elements fixes */
.content {
    padding-bottom: 100px;  /* Hauteur des elements fixes */
}

/* Ou avec margin */
.messages {
    margin-bottom: 100px;
}
```

### 4. Taskbar du systeme

```css
/* Sur Windows/Mac, la taskbar peut cacher le bas */
.status-bar {
    bottom: 45px;  /* Remonter pour eviter la taskbar */
}
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Quelle est la difference entre `position: fixed` et `position: absolute`?

<details>
<summary>Reponse</summary>
- **fixed**: Position par rapport au viewport (ecran). Ne bouge PAS avec le scroll.
- **absolute**: Position par rapport au parent positionne le plus proche. Peut sortir de l'ecran avec le scroll.

Fixed est ideal pour les elements UI qui doivent rester visibles.
</details>

### Question 2
Pourquoi faut-il ajouter `margin-bottom` au contenu?

<details>
<summary>Reponse</summary>
Les elements `position: fixed` sont retires du flux normal du document. Sans margin-bottom, le contenu passerait SOUS les elements fixes et serait invisible.

```css
.content {
    margin-bottom: 100px;  /* Espace pour input + status */
}
```
</details>

### Question 3
Comment eviter que l'input chevauche la sidebar?

<details>
<summary>Reponse</summary>

```css
.chat-input-container {
    position: fixed;
    left: 200px;  /* Commence apres la sidebar */
    right: 0;
}
```

Ou avec une variable CSS:
```css
left: var(--sidebar-width, 200px);
```
</details>

---

## Partie 7: Patterns de Position Fixed

### Pattern: Header + Footer fixes

```css
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
}

.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 40px;
}

.content {
    padding-top: 60px;
    padding-bottom: 40px;
}
```

### Pattern: FAB (Floating Action Button)

```css
.fab {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    z-index: 100;
}
```

### Pattern: Toast notifications

```css
.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
}
```

---

## Ressources Supplementaires

- [MDN: position](https://developer.mozilla.org/en-US/docs/Web/CSS/position)
- [CSS-Tricks: position](https://css-tricks.com/absolute-relative-fixed-positioining-how-do-they-differ/)
- [Z-index stacking](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Positioning/Understanding_z_index)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
