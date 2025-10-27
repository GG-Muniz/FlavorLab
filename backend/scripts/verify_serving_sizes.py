#!/usr/bin/env python3
"""
Quickly list serving_size_g (and source) for selected slugs or all ingredients.

Usage:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/verify_serving_sizes.py --slugs avocado,almonds
  # or all
  ./venv/Scripts/python.exe scripts/verify_serving_sizes.py
"""

import os
import sys
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.entity import Entity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--slugs', type=str, default='', help='Comma-separated slugs; if empty, prints all')
    args = parser.parse_args()

    wanted = [s.strip() for s in (args.slugs or '').split(',') if s.strip()]

    db = SessionLocal()
    try:
        q = db.query(Entity)
        if wanted:
            q = q.filter(Entity.slug.in_(wanted))
        rows = q.all()
        for ent in rows:
            attrs = ent.attributes or {}
            ss = attrs.get('serving_size_g')
            src = attrs.get('serving_size_g_source')
            print(f"{ent.slug or ent.id}: serving_size_g={ss} source={src}")
    finally:
        db.close()


if __name__ == '__main__':
    main()


