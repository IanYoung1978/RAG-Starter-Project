-- Runs once, the first time the database volume is created.
-- Turns on pgvector so tables can have "vector" columns for embeddings.
CREATE EXTENSION IF NOT EXISTS vector;
