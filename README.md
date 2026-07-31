# RAG-Starter-Project
RAG starter project using Python/Fast API, TS/Vue Frontend, Anthropic/Voyage AI, and postgresql

Project spec
Goal: working tool + learning vehicle for RAG concepts and a professional frontend workflow
Backend: Python, pip, FastAPI
LLM: Anthropic API (Claude) — field extraction, summary generation, gap analysis
Embeddings: Voyage AI
Storage: PostgreSQL + pgvector, running in a local Docker container
Frontend: Vue 3 + TypeScript, Vite, npm
Testing: Vitest + Vue Test Utils (frontend unit/component), pytest (backend), Playwright (e2e)
Tooling: ESLint + Prettier; Pinia deferred until prop-drilling actually hurts
CI: GitHub Actions
Repo: fresh — needs git init and a new GitHub repo
CV input: plain text / paste only for v1 (no PDF parsing yet)
