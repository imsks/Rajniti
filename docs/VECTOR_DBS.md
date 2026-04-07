# Vector databases and Chroma: basics for Rajniti

This document is a **learning guide** and an **implementation checklist** for bringing semantic search and (optionally) a Q&A bot back into Rajniti. Check items off as you complete them.

---

## 1. Why vector databases exist

Traditional databases are built for **exact** matches (IDs, ranges, joins). Many products also need **similarity**: “documents like this query” or “images like this one.” Those problems use **vectors** (lists of numbers) that capture meaning in a fixed-size space.

**Core ideas**

| Concept | What to remember |
|--------|-------------------|
| **Embedding** | A model turns text (or image, etc.) into a vector. Similar meanings → vectors that are close together (by distance). |
| **Vector DB** | Stores vectors + optional metadata and original text. Optimized for **nearest-neighbor search** (find the *k* closest vectors), often with filters (`where` clauses). |
| **Similarity / distance** | Common metrics: cosine similarity, L2 (Euclidean), inner product. Lower distance (or higher similarity) usually means “more alike.” |
| **Indexing** | Brute force over millions of vectors is slow. Systems use **approximate nearest neighbor (ANN)** indexes (e.g. HNSW, IVF) to trade a bit of recall for speed. |

**Mental model:** You are not “searching keywords” in the SQL sense; you are **searching in meaning-space** after both the query and the documents were embedded with the **same** embedding model.

---

## 2. How this differs from a normal search engine

- **Keyword / inverted index (e.g. Elasticsearch BM25):** great for literal terms and stemming.
- **Vector search:** great when users paraphrase or ask in natural language, as long as your embeddings were trained for that language/domain.

In practice, **hybrid** search (keyword + vector) often wins for production apps.

---

## 3. Chroma in one page

[Chroma](https://www.trychroma.com/) is an open-source **embedding database** aimed at developers building LLM apps. It is **not** a full document warehouse; it is focused on:

- **Collections** — named buckets of records.
- **Documents** — optional raw text you store for display/snippets.
- **Embeddings** — either you supply them or Chroma can call an embedding function (depending on setup).
- **Metadata** — JSON-serializable filters (e.g. `state`, `party`) for pre-filtering before or during search.

**Persistence**

- `PersistentClient(path=...)` stores data on disk (SQLite + segment files under the hood in typical local setups), so restarts keep your index.

**Query flow (typical)**

1. Embed the user query → one vector.
2. `query(query_embeddings=[...], n_results=k, where={...})` → nearest neighbors.
3. Return ids, documents, distances, metadatas.

**Internals (high level)**

- Storage and indexing evolve between versions; think **segments + ANN** rather than memorizing one algorithm. For learning depth, read Chroma’s docs and release notes for the version you pin.

---

## 4. Do you need an LLM provider?

**No, not for the vector database itself.**

| Piece | Needs cloud LLM? |
|-------|------------------|
| **Storing embeddings + metadata in Chroma** | No |
| **Embedding text** | No, if you use a **local** embedding model (e.g. via `sentence-transformers`, ONNX, or libraries that run on CPU/GPU locally) |
| **“Search only” UX** | No — return top chunks + metadata; user reads snippets |
| **Conversational answers that synthesize and cite** | Usually **yes** — that is **RAG**: retrieve with vectors, then **generate** text with an LLM (local or API) |

So: **syncing politician data into Chroma is 100% doable without any LLM API.** A **chatbot that paraphrases and explains** in natural language is where you add either a local model (e.g. Ollama) or a hosted API (Gemini, OpenAI, etc.).

---

## 5. Rajniti-specific architecture (target)

1. **Source of truth:** Postgres (or your existing politician JSON pipeline) → normalized politician records.
2. **Sync job:** Build a **text document per politician** (name, state, party, education bullets, criminal records summary, etc.), embed with a chosen model, **upsert** into Chroma with metadata `{ id, name, state, ... }`.
3. **Query path:** User question → embed with the **same** model → Chroma query → ranked results.
4. **Bot (later):** Optional LLM takes `(question, retrieved_chunks)` and returns a grounded answer; without LLM, return structured JSON + snippets only.

---

## Learning checklist (theory)

Use this section to track your reading and experiments. Mark items with `[x]` when done.

- [ ] Read one short explainer on **word embeddings** vs **sentence embeddings** (why dimensions are 384/768/etc.).
- [ ] Watch or read an intro to **cosine similarity** and why it is common for text vectors.
- [ ] Skim Chroma’s docs: **Collections**, **add/upsert**, **query**, **where filters**, **persistence**.
- [ ] Understand **ANN** vs exact k-NN in one paragraph (why ANN is used at scale).
- [ ] Read one comparison article: **vector DB vs keyword search** (when each helps).

---

## Implementation checklist (Rajniti)

These steps match how we will reintroduce Chroma **from scratch** in this repo.

### Dependencies and project wiring

- [ ] Add `chromadb` (pin a version) and an **embedding** dependency strategy (e.g. `fastembed`, `sentence-transformers`, or API embeddings — decide one).
- [ ] Add env vars: `CHROMA_DB_PATH`, `CHROMA_COLLECTION_NAME`, and embedding model name/path.
- [ ] Add `chroma_db/` (or your chosen path) to `.gitignore` if local DB should not be committed — or document an exception for dev-only samples.

### Core library

- [ ] Implement a small `VectorDB` wrapper: `PersistentClient`, `get_or_create_collection`, `upsert`, `query`, optional `reset_collection`.
- [ ] **Critical:** use the **same** embedding model for index and query; document the model id in `readme.md` or here.

### Sync pipeline

- [ ] New script: load politicians via `PoliticianService`, map each record → **document string** + **metadata dict** (include stable `id`).
- [ ] Batch `upsert` with embeddings (measure time on a laptop; tune batch size).
- [ ] Add a Makefile or `readme.md` snippet: how to run sync after data updates.

### API

- [ ] Restore `POST /api/v1/questions/ask` and `GET /api/v1/questions/<id>/answer` to call the vector layer (remove `501` stubs).
- [ ] Decide response shape: snippets only vs RAG summary field.

### Frontend / bot

- [ ] Ensure `useQuestions` / `useAskQuestion` handle success and error payloads (including empty results).
- [ ] If adding a bot UI: choose **retrieval-only** first, then optional LLM streaming.

### Quality and ops

- [ ] Unit tests with **mocked** Chroma client (avoid heavy deps in CI).
- [ ] Smoke test: one known query returns expected politician id.

---

## Quick reference: embedding the same thing twice

If you change the embedding model **after** building the index, you must **re-embed everything**. Treat model version as part of your deployment config.

---

## Further reading

- Chroma documentation: https://docs.trychroma.com/
- “ANN algorithms” overview (HNSW, IVF): search your favorite ML blog or Pinecone/Qdrant docs for intuition (concepts transfer).

When this checklist is mostly green, you will have both **understanding** and a **working** politician-aware semantic layer in Rajniti.
