#!/usr/bin/env python3
"""
Enrich entities.json with per-100g nutrition data for ingredients.

For each entity with primary_classification == "ingredient" that is missing
any of the required keys (calories, protein_g, carbs_g, fat_g), this script
will add values from a curated mapping when available, and report any that
remain unmapped so they can be completed manually.

Usage:
  python scripts/enrich_nutrition_data.py --write   # writes back to entities.json
  python scripts/enrich_nutrition_data.py           # dry run/report only

Notes:
  - Values are per 100 g and approximate, based on common nutrition databases.
  - Keys are stored under attributes as {"value": number} to match the app format.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings


REQUIRED = ("calories", "protein_g", "carbs_g", "fat_g")


def v(cals: float, p: float, c: float, f: float) -> Dict[str, Dict[str, float]]:
    return {
        "calories": {"value": round(float(cals), 2)},
        "protein_g": {"value": round(float(p), 2)},
        "carbs_g": {"value": round(float(c), 2)},
        "fat_g": {"value": round(float(f), 2)},
    }


# Curated approximate per-100g values
NUTRITION_MAP: Dict[str, Dict[str, Dict[str, float]]] = {
    # Fruits
    "Apples": v(52, 0.3, 14.0, 0.2),
    "Bananas": v(89, 1.1, 22.8, 0.3),
    "Blueberries": v(57, 0.7, 14.5, 0.3),
    "Cherries": v(63, 1.1, 16.0, 0.2),
    "Elderberries": v(73, 0.7, 18.4, 0.5),
    "Kiwi": v(61, 1.1, 14.7, 0.5),
    "Oranges": v(47, 0.9, 11.8, 0.1),
    "Citrus Fruits": v(45, 0.9, 11.5, 0.2),  # generic citrus average (per 100g)
    "Papaya": v(43, 0.5, 11.0, 0.3),
    "Pineapple": v(50, 0.5, 13.1, 0.1),
    "Pomegranate": v(83, 1.7, 18.7, 1.2),
    "Watermelon": v(30, 0.6, 7.6, 0.2),
    "Avocado": v(160, 2.0, 8.5, 14.7),
    # Berries & juices (approx)
    "Tart Cherries": v(50, 1.0, 12.2, 0.3),
    "Mixed Berries": v(50, 0.8, 12.0, 0.3),
    "Tart Cherry Juice": v(54, 0.3, 13.0, 0.1),
    "Beet Juice": v(43, 1.6, 10.0, 0.1),
    # Vegetables & fungi
    "Broccoli": v(34, 2.8, 6.6, 0.4),
    "Spinach": v(23, 2.9, 3.6, 0.4),
    "Sweet Potato": v(86, 1.6, 20.1, 0.1),
    "Beets": v(43, 1.6, 9.6, 0.2),
    "Red Bell Peppers": v(31, 1.0, 6.0, 0.3),
    "Tomatoes": v(18, 0.9, 3.9, 0.2),
    "Shiitake Mushrooms": v(34, 2.2, 6.8, 0.5),
    "Artichoke": v(47, 3.3, 10.5, 0.2),
    "Fennel": v(31, 1.2, 7.3, 0.2),
    "Dark Leafy Greens": v(30, 2.5, 5.0, 0.3),
    # Grains & legumes
    "Oats": v(389, 16.9, 66.3, 6.9),
    "Quinoa": v(368, 14.1, 64.2, 6.1),
    "Brown Rice": v(370, 7.9, 77.2, 2.9),
    "Whole Grains": v(360, 10.0, 72.0, 3.0),
    "Lentils": v(116, 9.0, 20.1, 0.4),  # cooked
    "Beans/Legumes": v(127, 8.7, 22.8, 0.5),  # cooked mixed
    # Nuts & seeds
    "Almonds": v(579, 21.2, 21.6, 49.9),
    "Walnuts": v(654, 15.2, 13.7, 65.2),
    "Mixed Nuts": v(607, 20.0, 21.0, 54.0),
    "Flax Seeds": v(534, 18.3, 28.9, 42.2),
    "Sunflower Seeds": v(584, 20.8, 20.0, 51.5),
    "Pumpkin Seeds": v(559, 30.2, 10.7, 49.1),
    "Chia Seeds": v(486, 16.5, 42.1, 30.7),
    # Animal products
    "Eggs": v(155, 12.6, 1.1, 10.6),
    "Chicken Breast": v(165, 31.0, 0.0, 3.6),
    "Turkey": v(189, 29.0, 0.1, 7.4),
    "Poultry": v(180, 27.0, 0.1, 7.0),
    "Beef Liver": v(175, 26.0, 4.0, 5.0),
    # Dairy
    "Milk": v(42, 3.4, 5.0, 1.0),  # 1% milk
    "Yogurt": v(59, 10.0, 3.6, 0.4),  # nonfat plain Greek (approx)
    "Greek Yogurt": v(59, 10.3, 3.6, 0.4),
    "Kefir": v(63, 3.6, 7.0, 2.0),
    "Cottage Cheese": v(98, 11.1, 3.4, 4.3),
    # Oils & sweets
    "Olive Oil EVOO": v(884, 0.0, 0.0, 100.0),
    "Honey": v(304, 0.3, 82.4, 0.0),
    "Dark Chocolate": v(546, 4.9, 61.0, 31.0),
    # Seafood
    "Salmon": v(208, 20.4, 0.0, 13.4),
    "Wild Salmon": v(182, 25.0, 0.0, 8.0),
    "Fatty Fish": v(200, 20.0, 0.0, 13.0),
    "Tuna": v(144, 23.3, 0.0, 4.9),
    "Oysters": v(68, 7.0, 4.0, 2.5),
    "Shellfish": v(99, 20.0, 1.5, 1.5),  # mixed shellfish
    # Herbs, teas, spices
    "Green Tea": v(1, 0.1, 0.0, 0.0),  # brewed
    "Chamomile Tea": v(1, 0.0, 0.2, 0.0),  # brewed
    "Peppermint": v(70, 3.8, 15.0, 0.9),  # fresh leaves
    "Passionflower": v(97, 0.0, 23.0, 0.7),  # generic fruit/leaf approx
    "Coffee": v(1, 0.1, 0.0, 0.0),  # brewed
    "Garlic": v(149, 6.4, 33.1, 0.5),
    "Ginger": v(80, 1.8, 18.0, 0.8),
    "Turmeric": v(354, 7.8, 64.9, 9.9),
    "Sauerkraut": v(19, 0.9, 4.3, 0.1),
    "Bone Broth": v(13, 2.6, 0.0, 0.2),  # varies widely
}


def ensure_attr(entity: Dict[str, Any]) -> Dict[str, Any]:
    attrs = entity.get("attributes") or {}
    entity["attributes"] = attrs
    return attrs


def merge_nutrition(attrs: Dict[str, Any], values: Dict[str, Dict[str, float]]) -> Tuple[bool, List[str]]:
    changed = False
    added: List[str] = []
    for k, val in values.items():
        if k not in attrs or attrs[k] is None:
            attrs[k] = val
            changed = True
            added.append(k)
    return changed, added


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich entities.json with nutrition data")
    parser.add_argument("--write", action="store_true", help="Write changes back to entities.json")
    args = parser.parse_args()

    settings = get_settings()
    data_path = Path(settings.json_data_path)
    entities_path = data_path / settings.entities_file

    if not entities_path.exists():
        print(f"entities.json not found at {entities_path}")
        return 1

    with entities_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    entities = data.get("entities") or []
    missing_before = 0
    updated = 0
    unmapped: List[str] = []

    for e in entities:
        if e.get("primary_classification") != "ingredient":
            continue
        attrs = e.get("attributes") or {}
        # Count missing
        if any(k not in attrs for k in REQUIRED):
            missing_before += 1
        name = e.get("name", "")
        values = NUTRITION_MAP.get(name)
        if not values:
            continue
        attrs = ensure_attr(e)
        changed, added_keys = merge_nutrition(attrs, values)
        if changed:
            updated += 1

    # After pass, collect remaining missing names
    for e in entities:
        if e.get("primary_classification") != "ingredient":
            continue
        attrs = e.get("attributes") or {}
        if any(k not in attrs for k in REQUIRED):
            unmapped.append(e.get("name", "(unknown)"))

    print("Nutrition Enrichment Report")
    print("=" * 29)
    print(f"Ingredients missing before: {missing_before}")
    print(f"Ingredients updated from mapping: {updated}")
    print(f"Ingredients still missing: {len(unmapped)}")
    if unmapped:
        print("Remaining to fill manually:")
        for n in sorted(set(unmapped)):
            print(f"- {n}")

    if args.write:
        with entities_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\nWrote changes to {entities_path}")
    else:
        print("\nDry run complete (no file changes). Use --write to save.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


