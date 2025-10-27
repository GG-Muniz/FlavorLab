#!/usr/bin/env python3
"""
Seed default ingredient categories into the database.

Run:
  cd FlavorLab/backend
  python scripts/seed_categories.py
"""

import os
import sys
from typing import List, Tuple

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.models import Category


DEFAULT_CATEGORIES: List[Tuple[str, str]] = [
    ("Produce", "produce"),
    ("Fruits", "fruits"),
    ("Berries", "berries"),
    ("Vegetables", "vegetables"),
    ("Leafy Greens", "leafy-greens"),
    ("Alliums", "alliums"),
    ("Root Vegetables", "root-vegetables"),
    ("Dairy", "dairy"),
    ("Meats", "meats"),
    ("Seafood", "seafood"),
    ("Grains", "grains"),
    ("Legumes", "legumes"),
    ("Nuts & Seeds", "nuts-seeds"),
    ("Herbs & Spices", "herbs-spices"),
    ("Oils", "oils"),
    ("Juices", "juices"),
    ("Fermented", "fermented"),
]


def ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def upsert_category(session, name: str, slug: str) -> None:
    existing = session.query(Category).filter(Category.slug == slug).first()
    if existing:
        if existing.name != name:
            existing.name = name
        return
    session.add(Category(name=name, slug=slug))


def main() -> None:
    print("Seeding default categories...")
    ensure_tables()
    db = SessionLocal()
    try:
        for name, slug in DEFAULT_CATEGORIES:
            upsert_category(db, name, slug)
        db.commit()
        print(f"✓ Seeded {len(DEFAULT_CATEGORIES)} categories")
    except Exception as e:
        db.rollback()
        print(f"Error seeding categories: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


