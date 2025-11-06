#!/usr/bin/env python3
"""
Patch selected ingredient display names without altering core IDs.

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/patch_display_names.py
"""

import os
import sys
from typing import Dict, List, Tuple

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import IngredientEntity
from app.models.entity import Entity as BaseEntity


# Rules: list of (matcher, replacement). Matcher is case-insensitive substring.
RULES: List[Tuple[str, str]] = [
    ("olive oil evoo", "Olive Oil"),
    ("fatty fish", "Fish"),
    ("beans/legumes", "Beans"),
]


def main() -> None:
    db = SessionLocal()
    updated = 0
    try:
        all_ings = db.query(IngredientEntity).all()
        for ing in all_ings:
            nm = (ing.name or "").lower()
            for needle, desired in RULES:
                if needle in nm:
                    name_changed = False
                    if ing.name != desired:
                        ing.name = desired
                        name_changed = True
                    if ing.display_name != desired:
                        ing.display_name = desired
                        name_changed = True
                    if name_changed:
                        updated += 1
                    break
        if updated:
            db.commit()
        print(f"Updated display_name on {updated} ingredients")
    finally:
        db.close()


if __name__ == "__main__":
    main()


