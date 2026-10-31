-- Tables for the brewing assistant. Safe to run more than once.
CREATE EXTENSION IF NOT EXISTS vector;

-- One row per Brewprint pack type (E1, X3, H4, D6, M44...) or extra ingredient.
CREATE TABLE IF NOT EXISTS ingredients (
    code         text PRIMARY KEY,        -- e.g. 'E5', or the name for extras like 'Wheat DME'
    category     text NOT NULL,           -- element, enhancer, hop_extract, dry_hop, additional, yeast
    name         text,                    -- hop variety for dry hops, e.g. 'Citra'
    description  text,
    pack_grams   integer,
    notes        text,
    in_stock     integer NOT NULL DEFAULT 0,   -- number of packs on hand
    embedding    vector(768)              -- filled in Phase 4 (nomic-embed-text makes 768 numbers)
);

-- One row per "Style Direction" recipe. The shorthand columns are kept exactly as written.
CREATE TABLE IF NOT EXISTS recipes (
    id               serial PRIMARY KEY,
    name             text NOT NULL UNIQUE,
    base             text,                -- e.g. 'E5 ×3 + E1 ×2'
    hop_layer        text,                -- e.g. 'H4 or H5'
    yeast            text,                -- e.g. 'M76'
    expected_result  text,
    embedding        vector(768)          -- filled in Phase 4
);

-- The recipe shorthand broken into clean rows. Filled in Phase 3 (structured output).
CREATE TABLE IF NOT EXISTS recipe_items (
    recipe_id          integer NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_code    text NOT NULL REFERENCES ingredients(code),
    quantity           integer NOT NULL DEFAULT 1,   -- packs
    role               text NOT NULL,                -- base, hops, yeast
    optional           boolean NOT NULL DEFAULT false,
    alternative_group  integer                       -- items sharing a number are "pick one", e.g. H1/H2
);
