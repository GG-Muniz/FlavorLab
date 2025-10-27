#!/usr/bin/env python3
"""Print a few ingredients with their image_url sources for debugging."""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import IngredientEntity


def main() -> None:
    db = SessionLocal()
    try:
        rows = db.query(IngredientEntity).order_by(IngredientEntity.name.asc()).limit(10).all()
        for ing in rows:
            attrs = ing.attributes or {}
            attr_img = None
            if isinstance(attrs.get("image_url"), dict):
                attr_img = attrs.get("image_url", {}).get("value")
            else:
                attr_img = attrs.get("image_url")
            print(
                f"{ing.id:20s} | name={ing.name:20s} | image_url={getattr(ing, 'image_url', None)} | attr_image_url={attr_img}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()


