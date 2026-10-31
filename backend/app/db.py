"""Database helpers."""

from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from app import config

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def connect() -> psycopg.Connection:
    # dict_row makes each result row a dict like {"code": "E1", ...}
    return psycopg.connect(config.DATABASE_URL, row_factory=dict_row)


def create_schema(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA_FILE.read_text())
