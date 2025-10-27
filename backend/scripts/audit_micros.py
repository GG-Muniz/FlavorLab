#!/usr/bin/env python3
"""
Audit vitamins & minerals (micronutrients) across ingredients.

Outputs a JSON report listing, per ingredient:
- missing_micros: True if no vitamins/minerals present
- has_macros_in_micros: True if macros (protein/fat/carbs) appear under micronutrients
- duplicates: any duplicated micronutrient names

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/audit_micros.py --out micronutrient_audit.json --summary
"""

import os
import sys
import json
import argparse
from typing import Any, Dict, List

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import IngredientEntity


MACRO_LIKE = {"protein", "proteins", "fat", "fats", "carb", "carbs", "carbohydrate", "carbohydrates"}


def normalize_name(n: Any) -> str:
    if isinstance(n, dict):
        name = n.get("nutrient_name") or n.get("name") or ""
    else:
        name = str(n or "")
    return name.strip()


def audit() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        items: List[Dict[str, Any]] = []
        for ing in db.query(IngredientEntity).all():
            attrs = getattr(ing, "attributes", {}) or {}
            micros = attrs.get("nutrient_references")
            if isinstance(micros, dict) and "value" in micros:
                micros = micros.get("value")
            names = [normalize_name(x) for x in (micros or [])]
            names_lower = [s.lower() for s in names]
            has_micros = any(n for n in names_lower if n and n not in MACRO_LIKE)
            has_macros = any(n in MACRO_LIKE for n in names_lower)
            duplicates = sorted({n for n in names if names_lower.count(n.lower()) > 1})

            items.append({
                "id": ing.id,
                "name": getattr(ing, "name", ing.id),
                "missing_micros": not has_micros,
                "has_macros_in_micros": has_macros,
                "duplicates": duplicates,
            })
        return {"items": items}
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, default='', help='Write report to JSON file')
    parser.add_argument('--summary', action='store_true', help='Print a concise summary to stdout')
    args = parser.parse_args()

    report = audit()
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Wrote report to {args.out}")

    if args.summary:
        items = report.get('items', [])
        missing = [i for i in items if i.get('missing_micros')]
        macros = [i for i in items if i.get('has_macros_in_micros')]
        dups = [i for i in items if i.get('duplicates')]
        print(f"Total ingredients: {len(items)}")
        print(f"Missing vitamins/minerals: {len(missing)}")
        print(f"Macros present in micronutrients: {len(macros)}")
        print(f"With duplicated micronutrients: {len(dups)}")

        if missing:
            print("\n— Missing (first 20):")
            for i in missing[:20]:
                print(f"  - {i['name']} ({i['id']})")
        if macros:
            print("\n— Macros listed as micros (first 20):")
            for i in macros[:20]:
                print(f"  - {i['name']} ({i['id']})")
        if dups:
            print("\n— Duplicates (first 20):")
            for i in dups[:20]:
                print(f"  - {i['name']} ({i['id']}): {', '.join(i['duplicates'])}")

    if not args.out and not args.summary:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()


