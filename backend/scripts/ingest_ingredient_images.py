#!/usr/bin/env python3
"""
Ingest and backfill ingredient image data and slugs.

For each ingredient entity:
  - Generate a slug from the name if missing
  - Compute a Cloudinary URL using configured base and folder
  - Optionally set display_name and aliases if provided by a mapping file

Usage:
  cd FlavorLab/backend
  python scripts/ingest_ingredient_images.py [--dry-run]

Environment/config:
  CLOUDINARY_BASE_URL or CLOUDINARY_CLOUD_NAME + constructed base
"""

import os
import sys
import argparse
import re
from typing import Optional, Dict, List, Set
import json
import urllib.parse
import hashlib
import hmac
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, Base, engine
from app.config import get_settings
from app.models import Entity, IngredientEntity, Category
# Robust import whether run as module or script
try:
    from .category_map import (
        NAME_TO_CATEGORY_SLUGS,
        SUBSTRING_RULES,
        CLASSIFICATION_TO_CATEGORY_SLUGS,
    )
except Exception:
    sys.path.insert(0, script_dir)
    from category_map import (  # type: ignore
        NAME_TO_CATEGORY_SLUGS,
        SUBSTRING_RULES,
        CLASSIFICATION_TO_CATEGORY_SLUGS,
    )


def slugify(name: str) -> str:
    value = name.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s-]+", "-", value).strip("-")
    return value


def cloudinary_base_url(settings) -> Optional[str]:
    if settings.cloudinary_base_url:
        return settings.cloudinary_base_url.rstrip("/")
    if settings.cloudinary_cloud_name:
        # Unsigned delivery base
        return f"https://res.cloudinary.com/{settings.cloudinary_cloud_name}/image/upload"
    return None


def build_image_url(base: str, folder: str, slug: str, settings, keyword_override: Optional[str] = None) -> str:
    # Provide a smart default transformation for thumbnails
    # f_auto: automatic format; q_auto: smart quality; c_fill,w_640,h_360 maintains 16:9 crop
    transform = "f_auto,q_auto,c_fill,w_640,h_360"

    # If configured, use Cloudinary fetch with Unsplash Source keyword per slug for dev/demo
    # Example: image/fetch/f_auto,q_auto,.../https%3A%2F%2Fsource.unsplash.com%2Ffeatured%2F%3Fblueberries
    if getattr(settings, "cloudinary_use_unsplash_fallback", False):
        # Use keywords derived from slug; replace dashes with commas to broaden search
        keywords = (keyword_override or slug).replace("-", ",")
        fetch_url = f"https://source.unsplash.com/featured/?{keywords}"
        if getattr(settings, "cloudinary_proxy_fetch", False):
            # Use image/fetch as proxy and URL-encode the remote URL
            if base.endswith("/image/upload"):
                fetch_base = base[:-len("/image/upload")] + "/image/fetch"
            else:
                fetch_base = f"https://res.cloudinary.com/{settings.cloudinary_cloud_name}/image/fetch"
            encoded = urllib.parse.quote(fetch_url, safe="")
            return f"{fetch_base}/{transform}/{encoded}"
        else:
            # Direct Unsplash Source URL; let the frontend load it as-is
            return fetch_url

    # Default: expect a public_id under our folder
    return f"{base}/{transform}/{folder}/{slug}.jpg"


def _collect_categories_by_slug(db) -> Dict[str, Category]:
    cats = db.query(Category).all()
    return {c.slug: c for c in cats}


def _infer_category_slugs(name: str, classifications: Optional[List[str]]) -> Set[str]:
    slugs: Set[str] = set()
    # Exact name mapping
    if name in NAME_TO_CATEGORY_SLUGS:
        slugs.update(NAME_TO_CATEGORY_SLUGS[name])

    # Classification hints
    for cls in (classifications or []):
        key = (cls or "").strip().lower()
        if key in CLASSIFICATION_TO_CATEGORY_SLUGS:
            slugs.add(CLASSIFICATION_TO_CATEGORY_SLUGS[key])

    # Substring heuristics
    lname = (name or "").lower()
    for slug, needles in SUBSTRING_RULES.items():
        if any(n in lname for n in needles):
            slugs.add(slug)
    return slugs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    base = cloudinary_base_url(settings)
    folder = (settings.cloudinary_folder or "flavorlab/ingredients").strip("/")

    if not base:
        print("CLOUDINARY_BASE_URL or CLOUDINARY_CLOUD_NAME must be configured.")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    # Load optional keyword overrides
    keywords_path = os.path.join(script_dir, 'image_keywords.json')
    slug_to_keywords: Dict[str, str] = {}
    try:
        if os.path.exists(keywords_path):
            with open(keywords_path, 'r', encoding='utf-8') as f:
                slug_to_keywords = json.load(f)
    except Exception as e:
        print(f"Warning: failed to load image_keywords.json: {e}")
    db = SessionLocal()
    updated = 0
    cat_assignments = 0
    try:
        slug_to_category = _collect_categories_by_slug(db)
        ingredients = db.query(IngredientEntity).all()
        for ing in ingredients:
            changed = False

            # Ensure slug
            if not getattr(ing, "slug", None):
                ing.slug = slugify(ing.name)
                changed = True

            # Ensure display_name defaults to name
            if not getattr(ing, "display_name", None):
                ing.display_name = ing.name
                changed = True

            # Ensure image_url (or update when using keyword overrides or cloud name mismatch)
            override = slug_to_keywords.get(ing.slug or "")
            current_url = getattr(ing, "image_url", None)
            must_rebuild = False
            if getattr(settings, "cloudinary_use_unsplash_fallback", False):
                must_rebuild = True
            elif current_url:
                if "res.cloudinary.com/demo" in current_url:
                    must_rebuild = True
                elif getattr(settings, "cloudinary_cloud_name", None):
                    expected_host = f"res.cloudinary.com/{settings.cloudinary_cloud_name}"
                    if expected_host not in current_url:
                        must_rebuild = True
            if must_rebuild or override or not current_url:
                ing.image_url = build_image_url(base, folder, ing.slug, settings, override)
                changed = True

            # Prepare category links
            desired_slugs = _infer_category_slugs(ing.name, getattr(ing, "classifications", []) or [])
            if desired_slugs:
                # Ensure relationship set exists
                existing_slugs = {c.slug for c in getattr(ing, "categories", []) or []}
                to_add = [slug for slug in desired_slugs if slug not in existing_slugs]
                for slug in to_add:
                    cat = slug_to_category.get(slug)
                    if cat:
                        ing.categories.append(cat)
                        changed = True
                        cat_assignments += 1

            if changed:
                updated += 1

        if args.dry_run:
            db.rollback()
            print(f"[DRY RUN] Would update {updated} ingredients and create {cat_assignments} category links")
        else:
            db.commit()
            print(f"Updated {updated} ingredients with slug/display/image_url and {cat_assignments} category links")
    except Exception as e:
        db.rollback()
        print(f"Error during ingestion: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


