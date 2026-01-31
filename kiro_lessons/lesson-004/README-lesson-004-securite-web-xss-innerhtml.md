# Cours 004: Sécurité Web - XSS innerHTML

## Niveau: Intermédiaire

## Durée estimée: 45-60 minutes

## Prérequis

- Bases de JavaScript
- Compréhension des vulnérabilités XSS
- Notions de sécurité web

---

## Partie 1: Énoncé du Problème

### Contexte

Tu travailles sur une application web qui affiche du contenu utilisateur. Un audit de sécurité a révélé une vulnérabilité XSS critique...

### Le fichier problématique

**Chemin**: `src/components/user_content.js`

**Fonction**: `displayUserContent()`

### Code avec la vulnérabilité

Voici le code actuel de la fonction (avec la vulnérabilité XSS):

```javascript
function displayUserContent(userInput) {
    const contentDiv = document.getElementById('user-content');
    // VULNÉRABILITÉ: innerHTML avec contenu non sanitisé
    contentDiv.innerHTML = userInput;
}
```

### Symptômes observés

1. Injection de scripts malveillants possible
2. Exécution de code JavaScript arbitraire
3. Vol potentiel de cookies et données sensibles
4. Défacement de la page web

---

## Partie 2: Ta Mission

### Objectif

Trouve et corrige la vulnérabilité XSS dans le code ci-dessus.

### Questions à te poser

1. Pourquoi `innerHTML` est-il dangereux avec du contenu utilisateur?
2. Quelles sont les alternatives sécurisées?
3. Comment sanitiser le contenu avant affichage?
4. Quels sont les autres vecteurs d'attaque XSS?

---

## Partie 3: Solution

### Le problème

L'utilisation d'`innerHTML` avec du contenu utilisateur non sanitisé permet l'injection de code JavaScript malveillant.

### La solution

Utiliser `textContent` ou sanitiser le contenu avant affichage:

```javascript
function displayUserContent(userInput) {
    const contentDiv = document.getElementById('user-content');
    // SÉCURISÉ: textContent échappe automatiquement le HTML
    contentDiv.textContent = userInput;
}
```

Ou avec sanitisation:

```javascript
function displayUserContent(userInput) {
    const contentDiv = document.getElementById('user-content');
    // SÉCURISÉ: sanitisation du contenu HTML
    const sanitizedInput = DOMPurify.sanitize(userInput);
    contentDiv.innerHTML = sanitizedInput;
}
```
