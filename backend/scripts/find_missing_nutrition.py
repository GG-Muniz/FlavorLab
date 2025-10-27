#!/usr/bin/env python3
"""
List ingredient slugs missing nutrition in the seed (and optionally compare out.json).

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/find_missing_nutrition.py --seed scripts/nutrition_seed.json --compare out.json
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Set

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import IngredientEntity


def load_items(path: str) -> Dict[str, Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f) or {}
    items = {}
    for it in data.get('items', []) or []:
        slug = (it.get('slug') or '').strip()
        if slug:
            items[slug] = it
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default='scripts/nutrition_seed.json')
    parser.add_argument('--compare', default='', help='Optional out.json to compare against')
    args = parser.parse_args()

    db = SessionLocal()
    try:
        db_slugs: Set[str] = set(i.slug for i in db.query(IngredientEntity).all() if i.slug)
    finally:
        db.close()

    seed_map = load_items(args.seed)
    seed_slugs = set(seed_map.keys())

    missing_in_seed = sorted(db_slugs - seed_slugs)
    print(f"DB slugs: {len(db_slugs)}, Seed slugs: {len(seed_slugs)}")
    print(f"Missing in seed ({len(missing_in_seed)}): {', '.join(missing_in_seed) if missing_in_seed else 'None'}")

    if args.compare:
        cmp_map = load_items(args.compare)
        cmp_slugs = set(cmp_map.keys())
        missing_in_out = sorted(db_slugs - cmp_slugs)
        print(f"Missing in out.json ({len(missing_in_out)}): {', '.join(missing_in_out) if missing_in_out else 'None'}")


if __name__ == '__main__':
    main()


