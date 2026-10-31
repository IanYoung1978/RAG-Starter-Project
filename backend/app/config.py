"""Settings read from environment variables (set in docker-compose.yml)."""

import os

DATABASE_URL = os.environ["DATABASE_URL"]
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "llama3.1:8b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
