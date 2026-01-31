# Cours 001: Bug Silencieux - Variable Non Initialisee

## Niveau: Debutant

## Duree estimee: 30-45 minutes

## Prerequis

- Bases de Python (variables, conditions, fonctions)
- Comprehension basique de SQL
- Savoir lire du code async/await (pas besoin de maitriser)

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur une application de gestion de contenu YouTube. L'administrateur a signale un bug etrange:

> "Quand j'accede au dashboard admin sans filtres, la liste de contenu est toujours vide, meme si la base de donnees contient des videos et des transcripts."

### Le fichier problematique

**Chemin**: `src/services/admin_service.py`

**Fonction**: `get_content_items()`

### Code avec le bug

Voici le code actuel de la fonction (avec le bug):

```python
async def get_content_items(self, filters: ContentFilter) -> Tuple[List[ContentItem], int]:
    """Get filtered content items with pagination"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            base_query = """
                SELECT 'video' as type, title, created_at FROM videos
                UNION ALL
                SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
            """

            # Build WHERE conditions safely
            where_conditions = []
            params = []

            if filters.content_type:
                where_conditions.append("type = ?")
                params.append(filters.content_type)

            if filters.search_query:
                where_conditions.append("title LIKE ?")
                params.append(f"%{filters.search_query}%")

            # Build final query
            if where_conditions:
                where_clause = " WHERE " + " AND ".join(where_conditions)
                full_query = f"SELECT * FROM ({base_query}) content{where_clause}"
            else:
                full_query = f"SELECT * FROM ({base_query}) content"

            # Get total count
            count_query = f"SELECT COUNT(*) FROM ({full_query}) counted"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # Get paginated results
            offset = (filters.page - 1) * filters.per_page
            query = f"""
                SELECT type, title, created_at, 'active' as status
                FROM (
                    SELECT 'video' as type, title, created_at FROM videos
                    UNION ALL
                    SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
                ) content
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([filters.per_page, offset])
            cursor.execute(query, params)

            items = []
            for row in cursor.fetchall():
                items.append(ContentItem(
                    id=f"{row[0]}_{hash(row[1])}",
                    title=row[1],
                    type=row[0],
                    created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                    status=row[3]
                ))

            return items, total_count
    except Exception as e:
        print(f"[ERROR] Failed to get content items: {e}")
        return [], 0
```

### Symptomes observes

1. L'endpoint `/api/admin/content` retourne `{"items": [], "total": 0}`
2. Aucune erreur visible dans les logs de l'application web
3. Le bug n'apparait QUE quand on n'applique aucun filtre
4. Avec un filtre (ex: `?content_type=video`), ca fonctionne!

---

## Partie 2: Ta Mission

### Objectif

Trouve et corrige le bug dans le code ci-dessus.

### Questions a te poser

1. Quelle variable est utilisee a la ligne `{where_clause}` dans la requete finale?
2. Dans quel cas cette variable est-elle definie?
3. Que se passe-t-il si `where_conditions` est une liste vide?
4. Pourquoi l'erreur est "silencieuse"?

### Indices (consulte seulement si tu bloques)

<details>
<summary>Indice 1: Portee des variables</summary>

En Python, une variable definie dans un bloc `if` n'existe que si ce bloc est execute.

```python
if condition:
    ma_variable = "definie"

print(ma_variable)  # Erreur si condition est False!
```

</details>

<details>
<summary>Indice 2: Le coupable</summary>

Regarde attentivement ou `where_clause` est definie vs ou elle est utilisee.

- Definie: Dans le bloc `if where_conditions:`
- Utilisee: Dans la requete `query` a la fin (ligne avec `{where_clause}`)

</details>

<details>
<summary>Indice 3: Pourquoi c'est silencieux?</summary>

Le bloc `try/except` capture TOUTES les exceptions et retourne `[], 0`.
Le `NameError` est donc "avale" sans laisser de trace visible.

</details>

---

## Partie 3: Exercice Pratique

### Etape 1: Reproduire le bug

```bash
# Lance l'application
cd /mnt/d/kiro
python -m uvicorn src.main:app --reload --port 8000

# Test sans filtre (devrait retourner des donnees mais retourne [])
curl http://localhost:8000/api/admin/content

# Test avec filtre (fonctionne!)
curl "http://localhost:8000/api/admin/content?content_type=video"
```

### Etape 2: Ajouter du debug

Modifie temporairement le code pour voir l'erreur:

```python
except Exception as e:
    print(f"[ERROR] Failed to get content items: {e}")
    import traceback
    traceback.print_exc()  # Ajoute cette ligne!
    return [], 0
```

Tu devrais maintenant voir:
```
NameError: name 'where_clause' is not defined
```

### Etape 3: Corriger le bug

Applique ta correction et verifie qu'elle fonctionne.

---

## Partie 4: Corrige (Solution Complete)

### Le probleme

La variable `where_clause` est definie UNIQUEMENT dans le bloc `if where_conditions:`.

Quand aucun filtre n'est applique:
- `where_conditions = []` (liste vide)
- `if where_conditions:` est `False` (liste vide = falsy)
- `where_clause` n'est JAMAIS definie
- Plus tard, `{where_clause}` dans le f-string cause un `NameError`

### La solution

Initialiser `where_clause` AVANT le bloc conditionnel:

```python
async def get_content_items(self, filters: ContentFilter) -> Tuple[List[ContentItem], int]:
    """Get filtered content items with pagination - BUG FIXED"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            base_query = """
                SELECT 'video' as type, title, created_at FROM videos
                UNION ALL
                SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
            """

            # ============================================
            # FIX: Initialiser where_clause AVANT le if
            # ============================================
            where_clause = ""  # <-- LIGNE AJOUTEE
            where_conditions = []
            params = []

            if filters.content_type:
                where_conditions.append("type = ?")
                params.append(filters.content_type)

            if filters.search_query:
                where_conditions.append("title LIKE ?")
                params.append(f"%{filters.search_query}%")

            # Build final query with initialized where_clause
            if where_conditions:
                where_clause = " WHERE " + " AND ".join(where_conditions)
                full_query = f"SELECT * FROM ({base_query}) content{where_clause}"
            else:
                full_query = f"SELECT * FROM ({base_query}) content"

            # Get total count
            count_query = f"SELECT COUNT(*) FROM ({full_query}) counted"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # Get paginated results
            offset = (filters.page - 1) * filters.per_page
            query = f"""
                SELECT type, title, created_at, 'active' as status
                FROM (
                    SELECT 'video' as type, title, created_at FROM videos
                    UNION ALL
                    SELECT 'transcript' as type, video_title as title, created_at FROM transcripts
                ) content
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([filters.per_page, offset])
            cursor.execute(query, params)

            items = []
            for row in cursor.fetchall():
                items.append(ContentItem(
                    id=f"{row[0]}_{hash(row[1])}",
                    title=row[1],
                    type=row[0],
                    created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                    status=row[3]
                ))

            return items, total_count
    except Exception as e:
        print(f"[ERROR] Failed to get content items: {e}")
        return [], 0
```

### Diff de la correction

```diff
  # Build WHERE conditions safely
+ where_clause = ""
  where_conditions = []
  params = []
```

Une seule ligne ajoutee!

---

## Partie 5: Lecons Apprises

### 1. Toujours initialiser les variables

```python
# MAUVAIS
if condition:
    result = "something"
return result  # NameError possible!

# BON
result = ""  # Valeur par defaut
if condition:
    result = "something"
return result  # Toujours defini
```

### 2. Attention aux exceptions silencieuses

```python
# DANGEREUX - avale toutes les erreurs
try:
    # code
except:
    return default_value

# MIEUX - au moins logger l'erreur
try:
    # code
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return default_value
```

### 3. Tester les cas limites

Toujours tester:
- Avec des filtres
- Sans filtres (liste vide)
- Avec des valeurs null/None

### 4. Le debugging systematique

Quand une fonction retourne silencieusement une valeur par defaut:
1. Ajouter `traceback.print_exc()` dans le except
2. Ou utiliser un debugger
3. Ou ajouter des print() temporaires

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi `if where_conditions:` est `False` quand la liste est vide?

<details>
<summary>Reponse</summary>
En Python, une liste vide `[]` est "falsy" - elle s'evalue a `False` dans un contexte booleen.
</details>

### Question 2
Pourquoi l'erreur n'apparaissait pas dans les logs?

<details>
<summary>Reponse</summary>
Le bloc `try/except` capture l'exception et retourne `[], 0` sans re-lever l'erreur. Le `print()` affiche le message mais pas le traceback complet.
</details>

### Question 3
Quelle autre solution aurait fonctionne?

<details>
<summary>Reponse</summary>
On aurait pu aussi ajouter un `else` explicite:

```python
if where_conditions:
    where_clause = " WHERE " + ...
else:
    where_clause = ""  # Explicite dans le else
```

Mais initialiser avant est plus clair et moins sujet aux oublis.
</details>

---

## Ressources Supplementaires

- [Python Variable Scope](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
- [Truthiness in Python](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- [Best Practices for Exception Handling](https://docs.python.org/3/tutorial/errors.html)

---

## Commit de Reference

```
Commit: (voir branche maitre-claude)
Message: fix(admin): Initialize where_clause before conditional - Issue 001
Fichier: src/services/admin_service.py
Ligne: 174
```

---

*Cours cree par @claude-opus-4.5 pour Blade Runner Academy*
*Date: 2026-01-11*
