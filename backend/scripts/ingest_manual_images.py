#!/usr/bin/env python3
"""
Ingest curated image URLs for specific slugs (manual override).

Usage:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/ingest_manual_images.py --file scripts/manual_image_urls.json --verbose
"""

import os
import sys
import json
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import Entity
from app.config import get_settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f) or {}
    items = data.get('items', []) or []

    db = SessionLocal()
    updated = 0
    settings = get_settings()
    cloud = (get_settings().cloudinary_cloud_name or '').strip() if hasattr(settings, 'cloudinary_cloud_name') else ''
    try:
        for it in items:
            slug = (it.get('slug') or '').strip()
            url = (it.get('image_url') or '').strip()
            public_id = (it.get('public_id') or '').strip()
            if not slug:
                continue
            if not url and public_id:
                if not cloud:
                    # Build basic URL without transformations if cloud not configured
                    url = f"https://res.cloudinary.com/{cloud}/image/upload/{public_id}"
                else:
                    url = f"https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto,c_fill,w_640,h_360/{public_id}"
            if not url:
                continue
            ent = db.query(Entity).filter(Entity.slug == slug).first()
            if not ent:
                ent = db.query(Entity).filter(Entity.id == slug).first()
            if not ent:
                if args.verbose:
                    print(f"skip {slug}: entity not found")
                continue
            ent.image_url = url
            updated += 1
        db.commit()
        print(f"Updated images for {updated} ingredients")
    finally:
        db.close()


if __name__ == '__main__':
    main()


