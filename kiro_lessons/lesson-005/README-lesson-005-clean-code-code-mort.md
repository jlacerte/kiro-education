# Cours 005: Clean Code - Code Mort

## Niveau: Debutant

## Duree estimee: 15-20 minutes

## Prerequis

- Bases de JavaScript
- Comprendre le DOM

---

## Partie 1: Enonce du Probleme

### Contexte

Tu fais une revue de code et tu trouves un morceau de JavaScript suspect dans le footer d'une page admin. Le code semble faire quelque chose, mais... est-ce vraiment le cas?

### Code suspect

**Fichier**: `templates/admin/base.html`

```javascript
// Initial status check
setTimeout(() => {
    document.querySelector('.admin-footer script').click();
}, 1000);
```

### Les questions a se poser

1. Que fait ce code exactement?
2. Est-ce que `.click()` sur un element `<script>` fait quelque chose?
3. Pourquoi ce code existe-t-il?

---

## Partie 2: Ta Mission

### Objectif

Determiner si ce code est utile ou mort, et le corriger.

### Definition: Code Mort

Le **code mort** (dead code) est du code qui:
- N'est jamais execute
- Est execute mais n'a aucun effet
- Fait reference a des elements qui n'existent pas
- Est commente mais jamais supprime

### Indices

<details>
<summary>Indice 1: Que fait .click() sur un script?</summary>

La methode `.click()` declenche un evenement "click" sur un element.
Mais les elements `<script>` ne reagissent pas aux clics!

```javascript
// Ceci ne fait RIEN:
document.querySelector('script').click();

// Les scripts s'executent au chargement, pas au clic
```

</details>

<details>
<summary>Indice 2: Pourquoi ce code existe?</summary>

C'est probablement un reste de debug ou une tentative ratee de:
- Declencher un rechargement de status
- Executer du code au demarrage

Le commentaire "Initial status check" suggere l'intention,
mais l'implementation est incorrecte.

</details>

<details>
<summary>Indice 3: Comment verifier?</summary>

Ouvre la console du navigateur et teste:

```javascript
document.querySelector('script').click();
// Aucun effet!
```

Compare avec un bouton:
```javascript
document.querySelector('button').click();
// Declenche le onclick du bouton
```

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Analyser le code

```bash
python exercice.py
```

L'analyseur va detecter le code mort.

### Etape 2: Comprendre pourquoi c'est inutile

Le code fait:
1. Attend 1 seconde (`setTimeout`)
2. Cherche un `<script>` dans `.admin-footer`
3. Appelle `.click()` dessus

Probleme: `.click()` sur `<script>` = rien!

### Etape 3: Corriger

Options:
- **Supprimer** le code mort (recommande)
- **Remplacer** par un vrai status check si necessaire

---

## Partie 4: Corrige (Solution Complete)

### Le probleme

```javascript
// Ce code NE FAIT RIEN:
document.querySelector('.admin-footer script').click();
```

Pourquoi?
- Les elements `<script>` n'ont pas de comportement de clic
- `.click()` declenche l'evenement, mais aucun handler n'ecoute
- Le script s'est deja execute au chargement de la page

### Solution A: Supprimer le code mort (Recommande)

```javascript
// Avant
setTimeout(() => {
    document.querySelector('.admin-footer script').click();
}, 1000);

// Apres: Rien! Ou juste un commentaire:
// Initial status check removed - clicking script elements has no effect
```

### Solution B: Remplacer par un vrai status check

Si l'intention etait de verifier le status:

```javascript
// Initial status check - version fonctionnelle
setTimeout(() => {
    fetch('/api/admin/health')
        .then(response => response.json())
        .then(data => {
            const statusEl = document.getElementById('admin-status');
            if (data.success) {
                statusEl.textContent = 'System OK';
                statusEl.classList.add('status-healthy');
            } else {
                statusEl.textContent = 'System Error';
                statusEl.classList.add('status-error');
            }
        })
        .catch(error => {
            console.error('Status check failed:', error);
        });
}, 1000);
```

---

## Partie 5: Lecons Apprises

### 1. Toujours questionner le code existant

```javascript
// Ce code fait-il vraiment ce que le commentaire dit?
// Initial status check
someCode();  // <- Verifier!
```

### 2. Types de code mort

| Type | Exemple | Detection |
|------|---------|-----------|
| Jamais execute | Code apres `return` | Linter |
| Sans effet | `.click()` sur script | Revue de code |
| Commente | `// oldFunction();` | Recherche manuelle |
| Inaccessible | Fonction jamais appelee | Coverage |

### 3. Pourquoi supprimer le code mort?

- **Lisibilite**: Moins de code = plus facile a lire
- **Maintenance**: Moins de code a maintenir
- **Confusion**: Le code mort peut induire en erreur
- **Performance**: Moins de code a charger (minime mais reel)

### 4. Outils de detection

```bash
# JavaScript
npx eslint --rule 'no-unused-vars: error' file.js

# Python
pip install vulture
vulture myproject/

# Coverage (code jamais execute)
pytest --cov=myproject --cov-report=html
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi `.click()` sur un element `<script>` ne fait rien?

<details>
<summary>Reponse</summary>
Les elements `<script>` n'ont pas de comportement de clic par defaut.
Le script s'execute au chargement de la page, pas en reponse a des evenements utilisateur.
`.click()` declenche un evenement "click", mais personne ne l'ecoute.
</details>

### Question 2
Comment detecter du code mort en JavaScript?

<details>
<summary>Reponse</summary>
- Linters (ESLint avec no-unused-vars, no-unreachable)
- Tests de couverture (code jamais execute)
- Revue de code manuelle
- Outils d'analyse statique
</details>

### Question 3
Faut-il toujours supprimer le code mort?

<details>
<summary>Reponse</summary>
Oui, dans la plupart des cas. Le code mort:
- Ajoute de la confusion
- Doit etre maintenu inutilement
- Peut contenir des bugs caches

Exception: Parfois on garde du code commente temporairement
pendant un refactoring, mais il doit etre supprime rapidement.
</details>

---

## Partie 7: Commandes de Verification

```bash
# Chercher du code mort potentiel (click sur script)
grep -rn "script.*click\|click.*script" templates/

# Chercher des fonctions jamais appelees
grep -rn "function " js/ | while read line; do
    func=$(echo $line | grep -oP 'function \K\w+')
    count=$(grep -r "$func" js/ | wc -l)
    if [ $count -eq 1 ]; then
        echo "Potentiellement mort: $func"
    fi
done

# Utiliser un linter
npx eslint --rule 'no-unused-vars: error' file.js
```

---

## Ressources Supplementaires

- [ESLint no-unused-vars](https://eslint.org/docs/rules/no-unused-vars)
- [Martin Fowler: Refactoring - Dead Code](https://refactoring.com/catalog/removeDeadCode.html)
- [Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
