#!/usr/bin/env python3
"""
Validate ingredient nutrition data in flavorlab.db

Checks that every entity with primary_classification == "ingredient" has
numeric values for the following attributes (per 100g):
  - calories
  - protein_g
  - carbs_g
  - fat_g

Usage:
  python scripts/validate_nutrition_data.py

Output:
  - Total ingredients checked
  - Missing keys report
  - Non-numeric/invalid values report
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure app package is importable when the script is run directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import Entity


REQUIRED_KEYS = ["calories", "protein_g", "carbs_g", "fat_g"]


def extract_value(attr: Any) -> Any:
    """Extract raw value from attribute entry.

    Attributes may be stored as:
      {"value": 42, ...} OR just a raw numeric value 42.
    """
    if isinstance(attr, dict) and "value" in attr:
        return attr.get("value")
    return attr


def is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


def validate_ingredient_attributes(attrs: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    missing: List[str] = []
    invalid: List[str] = []

    for key in REQUIRED_KEYS:
        if key not in (attrs or {}):
            missing.append(key)
            continue
        raw_value = extract_value(attrs.get(key))
        if raw_value is None or not is_number(raw_value):
            invalid.append(key)
    return missing, invalid


def main() -> int:
    session = SessionLocal()
    try:
        ingredients: List[Entity] = (
            session.query(Entity)
            .filter(Entity.primary_classification == "ingredient")
            .all()
        )

        total = len(ingredients)
        missing_report: List[str] = []
        invalid_report: List[str] = []

        for ing in ingredients:
            attrs = ing.attributes or {}
            missing, invalid = validate_ingredient_attributes(attrs)
            if missing:
                missing_report.append(f"- {ing.name} (missing: {', '.join(missing)})")
            if invalid:
                invalid_report.append(f"- {ing.name} (invalid: {', '.join(invalid)})")

        print("Nutrition Data Validation Report")
        print("=" * 34)
        print(f"Total ingredients checked: {total}")
        print("")
        if missing_report:
            print("Ingredients with missing keys:")
            print("\n".join(missing_report))
            print("")
        else:
            print("No missing keys detected.")
            print("")

        if invalid_report:
            print("Ingredients with non-numeric/null values:")
            print("\n".join(invalid_report))
        else:
            print("No invalid values detected.")

        # Non-zero exit if issues found (useful for CI), but keep friendly output
        return 1 if (missing_report or invalid_report) else 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())


