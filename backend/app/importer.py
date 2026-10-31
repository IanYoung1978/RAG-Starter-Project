"""Import the Brewprint spreadsheet into the database.

Run it inside the backend container:
    docker compose exec backend python -m app.importer /data/Brewprint_table_updated.xlsx

The sheet has two tables stacked on one tab: ingredients grouped under
section headings, then a "Style Direction" table of recipes. Running the
import again updates existing rows, so it's how stock changes get loaded.
"""

import sys

import openpyxl

from app.db import connect, create_schema

# Section heading in column A -> category stored in the database.
SECTIONS = {
    "Elements": "element",
    "Enhancers": "enhancer",
    "Hop extracts": "hop_extract",
    "Dry Hops": "dry_hop",
    "Additional Ingredients": "additional",
    "Mangrove Jack Yeasts": "yeast",
}
RECIPE_HEADING = "Style Direction"


def clean(value):
    """Turn blank cells into None and strip stray spaces."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def read_sheet(path: str) -> tuple[list[dict], list[dict]]:
    sheet = openpyxl.load_workbook(path, data_only=True).active
    ingredients, recipes = [], []
    category = None
    in_recipes = False

    for row in sheet.iter_rows(min_row=2, values_only=True):  # row 1 is the header
        first, second, third, fourth, fifth = (clean(c) for c in row[:5])
        if first is None:
            continue
        if first == RECIPE_HEADING:
            in_recipes = True
            continue
        if first in SECTIONS:
            category = SECTIONS[first]
            continue

        if in_recipes:
            recipes.append({
                "name": first,
                "base": second,
                "hop_layer": third,
                "yeast": fourth,
                "expected_result": fifth,
            })
        else:
            # Dry hop descriptions start with the variety: "Citra. Grapefruit, ..."
            name = second.split(".")[0] if category == "dry_hop" and second else None
            ingredients.append({
                "code": first,
                "category": category,
                "name": name,
                "description": second,
                "pack_grams": int(third) if third is not None else None,
                "notes": fourth,
                "in_stock": int(fifth or 0),
            })
    return ingredients, recipes


def save(ingredients: list[dict], recipes: list[dict]) -> None:
    with connect() as conn:  # one transaction: all rows load, or none do
        create_schema(conn)
        for item in ingredients:
            conn.execute(
                """
                INSERT INTO ingredients (code, category, name, description, pack_grams, notes, in_stock)
                VALUES (%(code)s, %(category)s, %(name)s, %(description)s, %(pack_grams)s, %(notes)s, %(in_stock)s)
                ON CONFLICT (code) DO UPDATE SET
                    category = EXCLUDED.category, name = EXCLUDED.name,
                    description = EXCLUDED.description, pack_grams = EXCLUDED.pack_grams,
                    notes = EXCLUDED.notes, in_stock = EXCLUDED.in_stock
                """,
                item,
            )
        for recipe in recipes:
            conn.execute(
                """
                INSERT INTO recipes (name, base, hop_layer, yeast, expected_result)
                VALUES (%(name)s, %(base)s, %(hop_layer)s, %(yeast)s, %(expected_result)s)
                ON CONFLICT (name) DO UPDATE SET
                    base = EXCLUDED.base, hop_layer = EXCLUDED.hop_layer,
                    yeast = EXCLUDED.yeast, expected_result = EXCLUDED.expected_result
                """,
                recipe,
            )


if __name__ == "__main__":
    ingredients, recipes = read_sheet(sys.argv[1])
    save(ingredients, recipes)
    print(f"Imported {len(ingredients)} ingredients and {len(recipes)} recipes.")
