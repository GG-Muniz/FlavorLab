#!/usr/bin/env python3
"""
Fetch per-100g nutrition for all ingredient slugs using USDA FoodData Central
and produce a nutrition_seed.json-like chunk you can merge.

Requires env FDC_API_KEY.

Run examples (PowerShell):
  cd FlavorLab/backend
  # Show progress for first 10
  ./venv/Scripts/python.exe scripts/generate_nutrition_from_fdc.py --limit 10 --verbose
  # Write all results to a file with progress
  ./venv/Scripts/python.exe scripts/generate_nutrition_from_fdc.py --verbose --out out.json
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Set
import requests
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import IngredientEntity
from app.config import get_settings


# FDC nutrient numbers per USDA documentation
# 208 Energy (kcal), 203 Protein, 205 Carbohydrate, 204 Fat, 291 Fiber, 269 Sugars
NUTRIENT_MAP = {
  'calories': 208,
  'protein_g': 203,
  'carbs_g': 205,
  'fat_g': 204,
  'fiber_g': 291,
  'sugars_g': 269
}


def search_fdc(api_key: str, query: str) -> Any:
    url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    params = {
        'api_key': api_key,
        'query': query,
        'pageSize': 5,
        'pageNumber': 1,
        'dataType': ['Survey (FNDDS)', 'SR Legacy', 'Branded'],
        'requireAllWords': True
    }
    r = requests.get(url, params=params, timeout=15, headers={'User-Agent': 'FlavorLab/1.0'})
    r.raise_for_status()
    return r.json()

def fetch_food_details(api_key: str, fdc_id: int) -> Any:
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = { 'api_key': api_key }
    r = requests.get(url, params=params, timeout=15, headers={'User-Agent': 'FlavorLab/1.0'})
    r.raise_for_status()
    return r.json()


def extract_per_100g(food: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for key, nutrient_id in NUTRIENT_MAP.items():
        val = None
        for n in food.get('foodNutrients', []) or []:
            num = str(n.get('nutrientNumber') or n.get('nutrient', {}).get('number') or '')
            nid = n.get('nutrientId')
            if num == str(nutrient_id) or nid == nutrient_id:
                val = n.get('value')
                break
        if val is not None:
            out[key] = float(val)
    return out


MICRO_KEYWORDS = [
  ("Calcium", "Calcium"),
  ("Iron", "Iron"),
  ("Magnesium", "Magnesium"),
  ("Phosphorus", "Phosphorus"),
  ("Potassium", "Potassium"),
  ("Sodium", "Sodium"),
  ("Zinc", "Zinc"),
  ("Copper", "Copper"),
  ("Manganese", "Manganese"),
  ("Vitamin C", "Vitamin C"),
  ("Vitamin B-6", "Vitamin B6"),
  ("Folate", "Folate")
]


def extract_micros(food: Dict[str, Any]) -> List[str]:
    """Return canonical micronutrient names present in the food item."""
    names: Set[str] = set()
    for n in food.get('foodNutrients', []) or []:
        label = (n.get('nutrientName') or n.get('nutrient', {}).get('name') or '').strip()
        if not label:
            continue
        for kw, canon in MICRO_KEYWORDS:
            if kw.lower() in label.lower():
                names.add(canon)
    return sorted(names)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0, help='Max number of slugs to process')
    parser.add_argument('--verbose', action='store_true', help='Print progress to stderr')
    parser.add_argument('--out', type=str, default='', help='Output file path (writes JSON)')
    parser.add_argument('--slugs', type=str, default='', help='Comma-separated slugs to process (subset)')
    parser.add_argument('--include-micros', action='store_true', help='Include serving_size_g when available (future micros)')
    args = parser.parse_args()
    settings = get_settings()
    api_key = (settings.fdc_api_key or '').strip()
    if not api_key:
        print('FDC_API_KEY is required')
        sys.exit(1)

    db = SessionLocal()
    try:
        slugs = [i.slug for i in db.query(IngredientEntity).all() if i.slug]
    finally:
        db.close()

    wanted = set(s.strip() for s in (args.slugs or '').split(',') if s.strip())
    if wanted:
        slugs = [s for s in slugs if s in wanted]

    results = []
    total = len(slugs)
    count = 0
    for idx, slug in enumerate(slugs, 1):
        query = slug.replace('-', ' ')
        if args.limit and count >= args.limit:
            break
        try:
            data = search_fdc(api_key, query)
            foods = (data or {}).get('foods', [])
            if foods:
                # Prefer SR Legacy / Survey items
                chosen = None
                for f in foods:
                    if f.get('dataType') in ('SR Legacy', 'Survey (FNDDS)'):
                        chosen = f
                        break
                if not chosen:
                    chosen = foods[0]
                per100 = extract_per_100g(chosen)
                micros = extract_micros(chosen)
                # Fetch full details to improve serving size extraction
                try:
                    details = fetch_food_details(api_key, int(chosen.get('fdcId')))
                except Exception:
                    details = None
                # Serving size grams if present on branded items
                if details:
                    try:
                        label_g = details.get('servingSize')
                        label_unit = (details.get('servingSizeUnit') or '').lower()
                        if isinstance(label_g, (int, float)) and label_g > 0 and label_unit in ('g', 'gram', 'grams'):
                            per100['serving_size_g'] = float(label_g)
                    except Exception:
                        pass
                    # For SR Legacy / FNDDS, use foodPortions gramWeight as a proxy
                    try:
                        if 'serving_size_g' not in per100:
                            portions = details.get('foodPortions') or details.get('foodMeasures') or []
                            # Prefer entries with gramWeight and a "serving" descriptor, otherwise take first gramWeight
                            candidate = None
                            for p in portions:
                                desc = (p.get('portionDescription') or p.get('modifier') or '').lower()
                                gw = p.get('gramWeight')
                                if isinstance(gw, (int, float)) and gw > 0 and ('serv' in desc or 'portion' in desc):
                                    candidate = gw
                                    break
                            if candidate is None:
                                for p in portions:
                                    gw = p.get('gramWeight')
                                    if isinstance(gw, (int, float)) and gw > 0:
                                        candidate = gw
                                        break
                            if candidate:
                                per100['serving_size_g'] = float(candidate)
                    except Exception:
                        pass
                if per100:
                    item = { 'slug': slug, **per100 }
                    if micros:
                        item['nutrient_references'] = micros
                    results.append(item)
                    count += 1
                    if args.verbose:
                        print(f"[{idx}/{total}] {slug} ✓", file=sys.stderr, flush=True)
                else:
                    if args.verbose:
                        print(f"[{idx}/{total}] {slug} (no nutrients)", file=sys.stderr, flush=True)
            time.sleep(0.4)
        except Exception as e:
            if args.verbose:
                print(f"[{idx}/{total}] skip {slug}: {e}", file=sys.stderr, flush=True)

    out_obj = { 'metadata': { 'unit': 'per_100g', 'source': 'fdc_api' }, 'items': results }
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(out_obj, f, indent=2)
        if args.verbose:
            print(f"Wrote {len(results)} items to {args.out}", file=sys.stderr, flush=True)
    else:
        print(json.dumps(out_obj, indent=2))


if __name__ == '__main__':
    main()


