"""Brewprint assistant API.

A health check, read-only views of the imported ingredients and recipes,
and /ask for questions to the model. Later phases add search, RAG and tools.
"""

import time

import httpx
import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

from app import config, llm
from app.db import connect
from app.prompts import SYSTEM_PROMPT, format_inventory

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
def list_ingredients(category: str | None = None, code: str | None = None, in_stock_only: bool = False) -> list[dict]:
    """List ingredients, optionally filtered by category (e.g. dry_hop) or stock."""
    sql = "SELECT code, category, name, description, pack_grams, notes, in_stock FROM ingredients WHERE true"
    params = {}
    if category:
        sql += " AND category = %(category)s"
        params["category"] = category
    if code:
        sql += " AND code = %(code)s"
        params["code"] = code
    if in_stock_only:
        sql += " AND in_stock > 0"
    with connect() as conn:
        return conn.execute(sql + " ORDER BY category, code", params).fetchall()


class AskRequest(BaseModel):
    question: str
    # Turn this off to see how the model answers with no knowledge of your data.
    include_inventory: bool = True


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    """Ask the model a question about your ingredients and recipes.

    Your whole sheet is small, so we simply paste all of it into the prompt
    ("context stuffing"). Phase 6 replaces this with retrieval, which sends
    only the relevant pieces.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    context = ""
    if request.include_inventory:
        with connect() as conn:
            ingredients = conn.execute("SELECT * FROM ingredients ORDER BY category, code").fetchall()
            recipes = conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
        context = format_inventory(ingredients, recipes)
        messages.append({"role": "user", "content": context})
    messages.append({"role": "user", "content": request.question})

    started = time.perf_counter()
    answer = llm.chat(messages)
    return {
        "answer": answer,
        "model": config.CHAT_MODEL,
        "context_characters": len(context),
        "seconds": round(time.perf_counter() - started, 1),
    }


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
