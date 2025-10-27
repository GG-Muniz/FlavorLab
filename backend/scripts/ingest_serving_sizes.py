#!/usr/bin/env python3
"""
Ingest manual serving sizes into Entity.attributes.

Usage:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/ingest_serving_sizes.py --file scripts/serving_sizes.json --verbose
"""

import os
import sys
import json
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.models.entity import Entity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default=os.path.join(script_dir, 'serving_sizes.json'))
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f) or {}
    items = data.get('items', []) or []

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    updated = 0
    try:
        for it in items:
            slug = (it.get('slug') or '').strip()
            if not slug:
                continue
            ent = db.query(Entity).filter(Entity.slug == slug).first()
            if not ent:
                ent = db.query(Entity).filter(Entity.id == slug).first()
            if not ent:
                if args.verbose:
                    print(f"skip {slug}: entity not found")
                continue
            attrs = ent.attributes or {}
            before = json.dumps(attrs, sort_keys=True, default=str)
            ss = it.get('serving_size_g')
            if ss is not None:
                attrs['serving_size_g'] = float(ss)
            if it.get('serving_size_g_source'):
                attrs['serving_size_g_source'] = it.get('serving_size_g_source')
            ent.attributes = attrs
            after = json.dumps(attrs, sort_keys=True, default=str)
            if before != after:
                updated += 1
        db.commit()
        print(f"Updated serving size for {updated} ingredients")
    finally:
        db.close()


if __name__ == '__main__':
    main()


