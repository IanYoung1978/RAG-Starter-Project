# RAG-Starter-Project

A homebrewing assistant built on a Brewprint ingredient and recipe table. It's a learning project for RAG and agentic patterns: structured output, search by meaning, hybrid search, tool use, workflows and an agent, all with open-weight models running locally.

Everything runs in Docker. Nothing is installed on the host apart from Docker Desktop.

## Stack

- **Backend:** Python, FastAPI
- **Models:** open-weight models served by [Ollama](https://ollama.com) in a container (GPU accelerated). Chat: Llama 3.1 8B. Embeddings: nomic-embed-text.
- **Storage:** PostgreSQL + pgvector
- **Frontend:** Vue 3 + TypeScript, Vite (Phase 8)
- **Testing:** pytest (backend), Vitest + Vue Test Utils (frontend), Playwright (end to end)
- **Tooling:** ESLint + Prettier; Pinia deferred until prop-drilling actually hurts
- **CI:** GitHub Actions

## Running it

You need Docker Desktop running. For GPU acceleration you also need an NVIDIA GPU and Docker Desktop's WSL 2 backend. Without a GPU, remove the `deploy` block under `ollama` in `docker-compose.yml`. It will still run, just slowly.

```bash
cp .env.example .env        # optional; the defaults work
docker compose up -d        # first run downloads ~6 GB of images and models
docker compose logs -f ollama-pull   # watch the model download
```

Then open http://localhost:8000/health. Every service should report `"ok": true`. The interactive API docs are at http://localhost:8000/docs.

To stop: `docker compose down`. To delete everything, including the database and models: `docker compose down -v`.

## Layout

```
backend/            FastAPI app (app/main.py), Dockerfile, requirements.txt
db/init.sql         turns on the pgvector extension
data/               source data to import (sheet export, brew notes)
frontend/           Vue app (Phase 8)
docker-compose.yml  all the services
```

## Data

- **Ingredients:** Brewprint packs. Elements (E1–E5), Enhancers (X1–X5), Hop extracts (H1–H9), Dry hops (D1–D8), extras and Mangrove Jack yeasts. Each has a description, pack weight and number of packs in stock.
- **Recipes ("Style Direction"):** a 5-bag base, hop layer, yeast and expected result, for example `E5 ×3 + E1 ×2`, `H4 or H5`, `M76`.
- **Brew notes:** one Markdown file per brew, giving search something real to work on.

Input is plain text and CSV only for v1.

## Build phases

0. Setup: containers, health check *(this phase)*
1. Database schema and import of the sheet
2. First model call
3. Structured output: parse recipe shorthand into rows
4. Embeddings
5. Search by meaning, then hybrid search
6. Ask the brew book (full RAG with sources)
7. Stock tools the model can call
8. Vue frontend
9. Recipe designer agent
10. Tests and CI
