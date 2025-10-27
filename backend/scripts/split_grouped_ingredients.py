#!/usr/bin/env python3
"""
Split grouped/aggregate ingredient slugs into singular ingredients and deactivate the generics.

This creates missing singular ingredients (if not present), keeps existing ones, and marks the
generic grouped slugs as inactive.

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/split_grouped_ingredients.py --verbose
"""

import os
import sys
import argparse
from typing import List, Dict

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.models.entity import Entity, IngredientEntity
from app.models.category import Category
from sqlalchemy import text
import json


# Mapping: grouped_slug -> { 'items': [ { 'name': ..., 'slug': ... } ], 'category_slugs': [...] }
GROUP_SPLITS: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    'citrus-fruits': {
        'items': [
            { 'name': 'Oranges', 'slug': 'oranges' },
            { 'name': 'Lemons', 'slug': 'lemons' },
            { 'name': 'Limes', 'slug': 'limes' },
            { 'name': 'Grapefruit', 'slug': 'grapefruit' },
        ],
        'category_slugs': ['fruits']
    },
    'dark-leafy-greens': {
        'items': [
            { 'name': 'Spinach', 'slug': 'spinach' },
            { 'name': 'Kale', 'slug': 'kale' },
            { 'name': 'Swiss Chard', 'slug': 'swiss-chard' },
        ],
        'category_slugs': ['vegetables']
    },
    'mixed-nuts': {
        'items': [
            { 'name': 'Almonds', 'slug': 'almonds' },
            { 'name': 'Walnuts', 'slug': 'walnuts' },
            { 'name': 'Cashews', 'slug': 'cashews' },
            { 'name': 'Pistachios', 'slug': 'pistachios' },
            { 'name': 'Hazelnuts', 'slug': 'hazelnuts' },
        ],
        'category_slugs': ['nuts']
    }
}


def get_categories(db, slugs: List[str]) -> List[Category]:
    if not slugs:
        return []
    rows = db.query(Category).filter(Category.slug.in_(slugs)).all()
    return rows


def ensure_ingredient(db, name: str, slug: str, categories: List[Category], verbose: bool = False) -> bool:
    """Create missing ingredient (Entity + IngredientEntity) and attach categories. Returns True if created."""
    ent = db.query(Entity).filter(Entity.slug == slug).first()
    if ent:
        # Already exists
        ingr = db.query(IngredientEntity).filter(IngredientEntity.id == ent.id).first()
        # If it exists only as base entity, add IngredientEntity row
        if not ingr:
            db.add(IngredientEntity(id=ent.id))
        # Attach categories if missing
        try:
            if hasattr(ingr, 'categories') and categories:
                for c in categories:
                    if c not in ingr.categories:
                        ingr.categories.append(c)
        except Exception:
            pass
        if verbose:
            print(f"kept {slug}")
        return False

    # Create fresh
    # Raw inserts to avoid mapper quirks
    db.execute(
        text(
            """
            INSERT INTO entities (id, name, slug, display_name, primary_classification, classifications, aliases, attributes, is_active, created_at, updated_at)
            VALUES (:id, :name, :slug, :display_name, :pc, :classifications, :aliases, :attributes, 1, datetime('now'), datetime('now'))
            """
        ),
        {
            'id': slug,
            'name': name,
            'slug': slug,
            'display_name': name,
            'pc': 'ingredient',
            'classifications': json.dumps(['ingredient']),
            'aliases': json.dumps([]),
            'attributes': json.dumps({})
        }
    )
    db.execute(text("INSERT INTO ingredient_entities (id) VALUES (:id)"), { 'id': slug })
    # Attach categories via join table
    for c in categories or []:
        db.execute(
            text("INSERT OR IGNORE INTO ingredient_categories (ingredient_id, category_id) VALUES (:iid, :cid)"),
            { 'iid': slug, 'cid': c.id }
        )
    if verbose:
        print(f"created {slug}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created = 0
    deactivated = 0
    try:
        for grouped_slug, cfg in GROUP_SPLITS.items():
            cats = get_categories(db, cfg.get('category_slugs') or [])
            items = cfg.get('items') or []
            for it in items:
                if ensure_ingredient(db, it['name'], it['slug'], cats, verbose=args.verbose):
                    created += 1
            # Deactivate generic if exists
            gen = db.query(Entity).filter(Entity.slug == grouped_slug).first()
            if gen and getattr(gen, 'is_active', True):
                gen.is_active = False
                deactivated += 1
        db.commit()
        print(f"Created {created} singular ingredients; deactivated {deactivated} grouped entries")
    finally:
        db.close()


if __name__ == '__main__':
    main()


