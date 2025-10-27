#!/usr/bin/env python3
"""
Force-reset ingredient image_url fields to direct Unsplash Source URLs.

This bypasses Cloudinary entirely to avoid 400 responses when proxying.
It uses curated keywords from image_keywords.json when available, otherwise
falls back to a simple slug-based query (dashes replaced by commas).

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/fix_image_urls.py
"""

import os
import sys
import json
from typing import Dict

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.models.entity import IngredientEntity


def load_keywords() -> Dict[str, str]:
    path = os.path.join(script_dir, 'image_keywords.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f) or {}
    except Exception:
        return {}


def build_unsplash_url(slug: str, keywords_map: Dict[str, str]) -> str:
    slug = (slug or '').strip()
    if not slug:
        return 'https://source.unsplash.com/featured/?food'
    q = keywords_map.get(slug)
    if not q:
        # broaden query by splitting slug by dashes
        q = slug.replace('-', ',')
    return f'https://source.unsplash.com/featured/?{q}'


def main() -> None:
    Base.metadata.create_all(bind=engine)
    keywords = load_keywords()
    db = SessionLocal()
    updated = 0
    try:
        items = db.query(IngredientEntity).all()
        for ing in items:
            slug = getattr(ing, 'slug', None) or ''
            # Always rewrite to direct Unsplash; front-end can render absolute URLs
            new_url = build_unsplash_url(slug, keywords)
            if getattr(ing, 'image_url', None) != new_url:
                ing.image_url = new_url
                updated += 1
        if updated:
            db.commit()
        print(f"Rewrote image_url for {updated} ingredients to direct Unsplash URLs")
    finally:
        db.close()


if __name__ == '__main__':
    main()


