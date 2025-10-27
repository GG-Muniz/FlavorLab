#!/usr/bin/env python3
"""
Split generic ingredient entities into granular ones and deactivate generics.

Example mappings:
  beanslegumes -> black-beans, kidney-beans, chickpeas, lentils
  mixed-berries -> strawberries, blueberries, raspberries, blackberries

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/split_generic_ingredients.py
"""

import os
import sys
from typing import List, Dict

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.models.entity import Entity, IngredientEntity
from app.models.category import Category
from sqlalchemy import text


SPLIT_MAP: Dict[str, Dict[str, List[str]]] = {
    # generic_slug: { 'names': [new names], 'category_slugs': [categories to attach] }
    'beanslegumes': {
        'names': ['Black Beans', 'Kidney Beans', 'Chickpeas', 'Lentils'],
        'category_slugs': ['legumes']
    },
    'mixed-berries': {
        'names': ['Strawberries', 'Blueberries', 'Raspberries', 'Blackberries'],
        'category_slugs': ['fruits', 'berries']
    }
}


def slugify(name: str) -> str:
    import re
    s = (name or '').strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s).strip('-')
    return s


def ensure_categories(db, slugs: List[str]) -> List[Category]:
    cats = []
    for slug in slugs:
        c = db.query(Category).filter(Category.slug == slug).first()
        if c:
            cats.append(c)
    return cats


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created = 0
    deactivated = 0
    try:
        for generic_slug, cfg in SPLIT_MAP.items():
            gen = db.query(Entity).filter(Entity.slug == generic_slug).first()
            if gen and getattr(gen, 'is_active', True):
                gen.is_active = False
                deactivated += 1
            names = cfg.get('names') or []
            cat_slugs = cfg.get('category_slugs') or []
            attach_cats = ensure_categories(db, cat_slugs)

            for name in names:
                new_slug = slugify(name)
                exists = db.query(Entity).filter(Entity.slug == new_slug).first()
                if exists:
                    continue
                # Use raw inserts to avoid mapper quirks
                db.execute(
                    text(
                        """
                        INSERT INTO entities (id, name, slug, display_name, primary_classification, classifications, attributes, is_active, created_at, updated_at)
                        VALUES (:id, :name, :slug, :display_name, :pc, :classifications, :attributes, 1, datetime('now'), datetime('now'))
                        """
                    ),
                    {
                        'id': new_slug,
                        'name': name,
                        'slug': new_slug,
                        'display_name': name,
                        'pc': 'ingredient',
                        'classifications': '[]',
                        'attributes': '{}'
                    }
                )
                db.execute(text("INSERT INTO ingredient_entities (id) VALUES (:id)"), { 'id': new_slug })
                # attach categories via join table
                for c in attach_cats:
                    db.execute(
                        text("INSERT OR IGNORE INTO ingredient_categories (ingredient_id, category_id) VALUES (:iid, :cid)"),
                        { 'iid': new_slug, 'cid': c.id }
                    )
                created += 1
        db.commit()
        print(f"Created {created} granular ingredients; deactivated {deactivated} generic ones")
    finally:
        db.close()


if __name__ == '__main__':
    main()


