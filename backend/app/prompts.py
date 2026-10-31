"""Prompts and the context we give the model.

A system prompt is the standing instructions sent with every question.
The model knows nothing about BrewArt's naming or your stock, so we tell it.
"""

SYSTEM_PROMPT = """You are a homebrewing assistant for someone who brews with BrewArt products.

BrewArt names each product with a code. The letter says what kind of product it is:
- E = element (the malt base of a beer), e.g. E5
- X = enhancer (adds body, sweetness, colour or alcohol), e.g. X3
- H = hop extract (bitterness and hop character), e.g. H4
- D = dry hop (aroma, added late), e.g. D6 is Citra
- Y = BrewArt yeast. Mangrove Jack yeasts use M codes, e.g. M44.
A recipe uses whole packs: "E5 ×3" means three packs of E5.

Rules:
- Answer only from the inventory and recipes provided. If they don't contain the answer, say so plainly.
- Never invent a product code or describe a code that isn't listed.
- Be brief and practical."""


def format_inventory(ingredients: list[dict], recipes: list[dict]) -> str:
    """Turn database rows into plain text the model can read."""
    lines = ["INVENTORY (code | category | description | packs in stock):"]
    for i in ingredients:
        lines.append(
            f"{i['code']} | {i['category']} | {i['description'] or 'no description'} | {i['in_stock']}"
        )
    lines.append("")
    lines.append("RECIPES (name | base | hops | yeast | expected result):")
    for r in recipes:
        lines.append(
            f"{r['name']} | {r['base']} | {r['hop_layer']} | {r['yeast']} | {r['expected_result'] or ''}"
        )
    return "\n".join(lines)
