"""Brewprint assistant API.

Phase 0 only has a health check, which proves the backend can reach the
database and the model server. Later phases add search, RAG and tools.
"""

import httpx
import psycopg
from fastapi import FastAPI

from app import config

app = FastAPI(title="Brewing assistant")


@app.get("/health")
def health() -> dict:
    """Report whether each service the app depends on is reachable."""
    return {
        "database": check_database(),
        "ollama": check_ollama(),
        "chat_model": config.CHAT_MODEL
    }


def check_database() -> dict:
    try:
        with psycopg.connect(config.DATABASE_URL, connect_timeout=3) as conn:
            row = conn.execute(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
            ).fetchone()
        return {"ok": True, "pgvector": row[0] if row else None}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_ollama() -> dict:
    try:
        response = httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=3)
        response.raise_for_status()
        installed = [m["name"] for m in response.json()["models"]]
        wanted = [config.CHAT_MODEL, config.EMBED_MODEL]
        # Ollama adds ":latest" to names given without a tag.
        missing = [
            w for w in wanted if w not in installed and f"{w}:latest" not in installed
        ]
        return {"ok": not missing, "installed": installed, "missing": missing}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
