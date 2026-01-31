# Cours 010: Recherche Multi-Sources (KB + Index Video)

## Niveau: Intermediaire

## Duree estimee: 35-45 minutes

## Prerequis

- Bases de Python
- Notions de bases de donnees (SQL)
- Comprendre les recherches full-text

---

## Partie 1: Enonce du Probleme

### Contexte

Tu travailles sur un chatbot AI qui repond aux questions sur des videos YouTube. L'utilisateur demande: "What videos do you have about RAG?"

### Comportement actuel

```
User: "What videos about RAG?"
     |
     v
Chat cherche dans: Knowledge Base (transcripts)
     |
     v
Resultat: "I found 1 video about RAG"
          (mais l'utilisateur a 5 videos sur RAG dans ses subscriptions!)
```

### Le probleme

Le chat ne cherche que dans la **Knowledge Base** (videos dont les transcripts ont ete telecharges). Il ignore les videos dans l'**index YouTube** qui n'ont pas encore de transcript.

### Code problematique

```python
class ChatService:
    def search(self, query: str) -> List[Video]:
        # Cherche SEULEMENT dans la KB
        return self.kb.search(query)

    # Les videos sans transcript sont IGNOREES!
```

---

## Partie 2: Ta Mission

### Objectif

Faire en sorte que le chat cherche dans DEUX sources:
1. **Knowledge Base** (transcripts existants) -> Reponse AI detaillee
2. **Video Index** (videos sans transcript) -> Boutons de telechargement

### Workflow desire

```
User: "What videos about RAG?"
     |
     v
Chat cherche dans:
  1. KB (transcripts) -> Reponse AI
  2. video_index (videos sans transcript) -> Suggestions
     |
     v
Resultat:
  AI: "Based on the transcript of 'RAG Tutorial',
       here's what I found..."

  Related videos available:
  [Build a RAG Agent] [Download]
  [RAG Best Practices] [Download]
```

### Questions a se poser

1. Comment structurer la recherche multi-sources?
2. Comment differencier les resultats (avec/sans transcript)?
3. Comment permettre le telechargement a la demande?

---

## Partie 3: Exercice Pratique

### Etape 1: Comprendre le probleme

```bash
python exercice.py
```

### Etape 2: Implementer la solution

1. Ajouter la recherche dans `video_index`
2. Filtrer les videos sans transcript
3. Combiner les resultats

### Indices

<details>
<summary>Indice 1: Structure de video_index</summary>

```sql
CREATE TABLE video_index (
    video_id TEXT PRIMARY KEY,
    title TEXT,
    channel_name TEXT,
    description TEXT,
    transcript_synced BOOLEAN DEFAULT FALSE
);

CREATE VIRTUAL TABLE video_index_fts USING fts5(
    title, description, channel_name,
    content=video_index
);
```

</details>

<details>
<summary>Indice 2: Recherche FTS5</summary>

```python
def search_video_index(query: str) -> List[Video]:
    sql = """
    SELECT v.* FROM video_index v
    JOIN video_index_fts fts ON v.video_id = fts.rowid
    WHERE video_index_fts MATCH ?
    AND v.transcript_synced = FALSE
    """
    return db.execute(sql, (query,)).fetchall()
```

</details>

<details>
<summary>Indice 3: Combiner les resultats</summary>

```python
def search_all(query: str) -> dict:
    return {
        "kb_results": self.kb.search(query),  # Avec transcript
        "suggestions": self.video_index.search(query)  # Sans transcript
    }
```

</details>

---

## Partie 4: Corrige (Solution Complete)

### Structure de la solution

```python
class ChatService:
    def __init__(self, kb: KnowledgeBase, video_index: VideoIndex):
        self.kb = kb
        self.video_index = video_index

    def search(self, query: str) -> SearchResults:
        # 1. Chercher dans la KB (transcripts existants)
        kb_results = self.kb.search(query)

        # 2. Chercher dans l'index (videos sans transcript)
        index_results = self.video_index.search(query)

        # 3. Filtrer les videos deja dans la KB
        kb_video_ids = {v.video_id for v in kb_results}
        suggestions = [
            v for v in index_results
            if v.video_id not in kb_video_ids
            and not v.transcript_synced
        ]

        return SearchResults(
            kb_results=kb_results,
            suggestions=suggestions
        )
```

### Rendu de la reponse

```python
def render_response(self, results: SearchResults, query: str) -> str:
    response_parts = []

    # Partie 1: Reponse AI basee sur les transcripts
    if results.kb_results:
        ai_response = self.generate_ai_response(
            query=query,
            context=results.kb_results
        )
        response_parts.append(ai_response)

    # Partie 2: Suggestions de videos a telecharger
    if results.suggestions:
        response_parts.append("\n\nRelated videos available:")
        for video in results.suggestions[:5]:
            response_parts.append(
                f"  [{video.title}] [Download]"
            )

    return "\n".join(response_parts)
```

---

## Partie 5: Lecons Apprises

### 1. Penser aux sources de donnees multiples

```python
# MAUVAIS - Une seule source
results = kb.search(query)

# BON - Plusieurs sources combinees
results = {
    "primary": kb.search(query),
    "secondary": video_index.search(query),
    "external": youtube_api.search(query)  # Optionnel
}
```

### 2. Telechargement a la demande

```python
# Ne pas tout telecharger d'avance
# Laisser l'utilisateur choisir

@app.post("/api/download/{video_id}")
async def download_transcript(video_id: str):
    # Telecharge seulement quand l'utilisateur clique
    transcript = await youtube.get_transcript(video_id)
    await kb.add(video_id, transcript)
    return {"status": "success"}
```

### 3. Feedback progressif

```
Etape 1: Reponse immediate (KB existante)
    "Here's what I know about RAG..."

Etape 2: Suggestions (index video)
    "I found more videos you might want to explore"

Etape 3: Action utilisateur (download)
    User clique -> Transcript telecharge -> Ajout a la KB
```

### 4. Index FTS5 pour la performance

```sql
-- Recherche rapide meme avec des milliers de videos
CREATE VIRTUAL TABLE video_index_fts USING fts5(
    title,
    description,
    channel_name
);

-- Requete en ~1ms meme sur 10,000 videos
SELECT * FROM video_index_fts WHERE video_index_fts MATCH 'RAG';
```

---

## Partie 6: Quiz d'Auto-Evaluation

### Question 1
Pourquoi chercher dans plusieurs sources?

<details>
<summary>Reponse</summary>
Une seule source peut avoir des donnees incompletes. Dans notre cas:
- La KB ne contient que les transcripts telecharges
- L'index video contient TOUTES les videos

En combinant les deux, on donne a l'utilisateur une vue complete de ce qui est disponible.
</details>

### Question 2
Pourquoi utiliser FTS5 au lieu de LIKE?

<details>
<summary>Reponse</summary>

```sql
-- LIKE: Lent, O(n), pas de ranking
SELECT * FROM videos WHERE title LIKE '%RAG%';

-- FTS5: Rapide, O(log n), ranking automatique
SELECT * FROM videos_fts WHERE videos_fts MATCH 'RAG';
```

FTS5 est 100x plus rapide et supporte:
- Recherche par mots-cles
- Ranking par pertinence
- Operateurs booleens (AND, OR, NOT)
</details>

### Question 3
Pourquoi telecharger a la demande plutot que tout d'avance?

<details>
<summary>Reponse</summary>
- Economie de bande passante (API YouTube limitee)
- Economie de stockage
- L'utilisateur ne s'interesse qu'a certaines videos
- Experience plus rapide (pas d'attente initiale)
</details>

---

## Partie 7: Patterns de Recherche

### Pattern: Recherche federee

```python
class FederatedSearch:
    def __init__(self, sources: List[SearchSource]):
        self.sources = sources

    async def search(self, query: str) -> List[Result]:
        # Chercher dans toutes les sources en parallele
        tasks = [source.search(query) for source in self.sources]
        results = await asyncio.gather(*tasks)

        # Combiner et dedupliquer
        combined = []
        seen_ids = set()
        for result_list in results:
            for result in result_list:
                if result.id not in seen_ids:
                    combined.append(result)
                    seen_ids.add(result.id)

        return combined
```

### Pattern: Recherche avec fallback

```python
async def search_with_fallback(query: str) -> List[Result]:
    # Essayer la source principale
    results = await primary_source.search(query)

    if not results:
        # Fallback sur source secondaire
        results = await secondary_source.search(query)

    if not results:
        # Fallback sur recherche externe
        results = await external_api.search(query)

    return results
```

---

## Ressources Supplementaires

- [SQLite FTS5](https://www.sqlite.org/fts5.html)
- [Full-Text Search Explained](https://www.postgresql.org/docs/current/textsearch.html)
- [Federated Search Pattern](https://martinfowler.com/articles/data-mesh-principles.html)

---

*Cours cree par @claude-opus-4.5 pour Kiro Academy*
*Date: 2026-01-11*
