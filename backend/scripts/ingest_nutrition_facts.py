#!/usr/bin/env python3
"""
Ingest nutrition facts per 100g from nutrition_seed.json into Entity.attributes
with a flattened format (calories: number, protein_g: number, etc.).

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/ingest_nutrition_facts.py
"""

import os
import sys
import json
from typing import Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.models.entity import Entity
from sqlalchemy import func


SEED_PATH = os.path.join(script_dir, 'nutrition_seed.json')

# Known alias → canonical slug resolver
ALIAS_TO_SLUG = {
    "beans": "beanslegumes",
}

def load_seed() -> Dict[str, Any]:
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def coerce_number(value: Any):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def upsert_flat_attribute(entity: Entity, key: str, value):
    if entity.attributes is None:
        entity.attributes = {}
    # Flattened preferred
    entity.attributes[key] = value


def ingest() -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    updated = 0
    try:
        data = load_seed()
        items = data.get('items', [])
        for item in items:
            slug = (item.get('slug') or '').strip()
            if not slug:
                continue
            # Resolve aliases first
            resolved_slug = ALIAS_TO_SLUG.get(slug, slug)

            # Find by slug stored in Entity.slug or by id fallback
            entity = db.query(Entity).filter(Entity.slug == resolved_slug).first()
            if not entity:
                # Try fallback by name id match
                entity = db.query(Entity).filter(Entity.id == resolved_slug).first()
            if not entity:
                # Last resort: name-based fuzzy match (case-insensitive, spaces vs dashes)
                name_like = resolved_slug.replace('-', ' ')
                entity = (
                    db.query(Entity)
                    .filter(func.lower(Entity.name).like(f"%{name_like.lower()}%"))
                    .first()
                )
            if not entity:
                print(f"skip {slug}: entity not found")
                continue

            before = json.dumps(entity.attributes or {}, sort_keys=True, default=str)

            # Coerce and set (include serving_size_g and micronutrients if available)
            for key in ['calories', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g', 'sugars_g', 'serving_size_g']:
                if key in item:
                    val = coerce_number(item.get(key))
                    if val is not None:
                        if key == 'serving_size_g':
                            # Preserve manual serving sizes as authoritative
                            existing_source = None
                            if entity.attributes and isinstance(entity.attributes, dict):
                                existing_source = entity.attributes.get('serving_size_g_source')
                            if existing_source == 'manual':
                                # Skip overwrite
                                pass
                            else:
                                upsert_flat_attribute(entity, key, val)
                                # Track source for future reference (not displayed)
                                entity.attributes = entity.attributes or {}
                                entity.attributes['serving_size_g_source'] = 'fdc'
                        else:
                            upsert_flat_attribute(entity, key, val)

            # Micronutrient names (list of strings) if present
            if 'nutrient_references' in item and isinstance(item['nutrient_references'], list):
                entity.attributes = entity.attributes or {}
                entity.attributes['nutrient_references'] = item['nutrient_references']

            after = json.dumps(entity.attributes or {}, sort_keys=True, default=str)
            if before != after:
                updated += 1
        db.commit()
        return updated
    finally:
        db.close()


def main() -> None:
    updated = ingest()
    print(f"Updated nutrition facts for {updated} entities")


if __name__ == '__main__':
    main()


