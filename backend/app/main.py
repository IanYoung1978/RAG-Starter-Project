"""Brewprint assistant API.

A health check, plus read-only views of the imported ingredients and
recipes. Later phases add search, RAG and tools.
"""

import httpx
import psycopg
from fastapi import FastAPI

from app import config
from app.db import connect

app = FastAPI(title="Brewing assistant")


@app.get("/health")
def health() -> dict:
    """Report whether each service the app depends on is reachable."""
    return {
        "database": check_database(),
        "ollama": check_ollama(),
        "chat_model": config.CHAT_MODEL
    }


@app.get("/ingredients")
def list_ingredients(category: str | None = None, in_stock_only: bool = False) -> list[dict]:
    """List ingredients, optionally filtered by category (e.g. dry_hop) or stock."""
    sql = "SELECT code, category, name, description, pack_grams, notes, in_stock FROM ingredients WHERE true"
    params = {}
    if category:
        sql += " AND category = %(category)s"
        params["category"] = category
    if in_stock_only:
        sql += " AND in_stock > 0"
    with connect() as conn:
        return conn.execute(sql + " ORDER BY category, code", params).fetchall()


@app.get("/recipes")
def list_recipes() -> list[dict]:
    """List recipes with their shorthand exactly as written in the sheet."""
    with connect() as conn:
        return conn.execute(
            "SELECT id, name, base, hop_layer, yeast, expected_result FROM recipes ORDER BY name"
        ).fetchall()


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
