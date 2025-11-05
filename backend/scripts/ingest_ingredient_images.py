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

import argparse
import json
import os
import re
import sys
import urllib.parse
from typing import Dict, List, Optional, Set

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


def _bool_from_env(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def build_image_url(base: str, folder: str, slug: str, settings, keyword_override: Optional[str] = None, *, use_unsplash: Optional[bool] = None, proxy_fetch: Optional[bool] = None) -> str:
    # Provide a smart default transformation for thumbnails
    # f_auto: automatic format; q_auto: smart quality; c_fill,w_640,h_360 maintains 16:9 crop
    transform = "f_auto,q_auto,c_fill,w_640,h_360"

    # If configured, use Cloudinary fetch with Unsplash Source keyword per slug for dev/demo
    # Example: image/fetch/f_auto,q_auto,.../https%3A%2F%2Fsource.unsplash.com%2Ffeatured%2F%3Fblueberries
    if use_unsplash is None:
        use_unsplash = getattr(settings, "cloudinary_use_unsplash_fallback", False)
    if proxy_fetch is None:
        proxy_fetch = getattr(settings, "cloudinary_proxy_fetch", False)

    if use_unsplash:
        # Use keywords derived from slug; replace dashes with commas to broaden search
        keywords = (keyword_override or slug).replace("-", ",")
        fetch_url = f"https://source.unsplash.com/featured/?{keywords}"
        if proxy_fetch:
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

    # Ingredient-specific overrides (fallback to legacy single-variable config)
    env_folder = os.environ.get("CLOUDINARY_INGREDIENT_FOLDER")
    folder_setting = getattr(settings, "cloudinary_ingredient_folder", None)
    folder_candidate = env_folder or folder_setting or getattr(settings, "cloudinary_folder", None)
    if not env_folder and folder_candidate and "apothecary" in folder_candidate and "ingredients" not in folder_candidate:
        folder_candidate = folder_candidate.replace("apothecary", "ingredients")
    folder = (folder_candidate or "healthlab/ingredients").strip("/")

    env_use_unsplash = os.environ.get("CLOUDINARY_INGREDIENT_USE_UNSPLASH")
    ingredient_use_unsplash = _bool_from_env(env_use_unsplash, True)

    env_proxy_fetch = os.environ.get("CLOUDINARY_INGREDIENT_PROXY_FETCH")
    ingredient_proxy_fetch = _bool_from_env(env_proxy_fetch, getattr(settings, "cloudinary_proxy_fetch", False))

    base = cloudinary_base_url(settings)

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

    # Load serving size data if available
    serving_sizes_path = os.path.join(script_dir, 'serving_sizes.json')
    slug_to_serving: Dict[str, Dict[str, any]] = {}
    try:
        if os.path.exists(serving_sizes_path):
            with open(serving_sizes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('items', []):
                    slug = item.get('slug')
                    if slug:
                        slug_to_serving[slug] = item
    except Exception as e:
        print(f"Warning: failed to load serving_sizes.json: {e}")

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
            should_set_image = override or not current_url
            if should_set_image:
                ing.image_url = build_image_url(
                    base,
                    folder,
                    ing.slug,
                    settings,
                    override,
                    use_unsplash=ingredient_use_unsplash,
                    proxy_fetch=ingredient_proxy_fetch,
                )
                changed = True

            # Ensure serving size metadata
            serving_info = slug_to_serving.get(ing.slug or "")
            if serving_info:
                target_value = serving_info.get("serving_size_g")
                source_value = serving_info.get("serving_size_g_source")
                attrs: Dict[str, Dict[str, any]] = ing.attributes or {}
                current_serving = attrs.get("serving_size_g", {}).get("value") if isinstance(attrs.get("serving_size_g"), dict) else attrs.get("serving_size_g")
                if target_value and current_serving != target_value:
                    attrs["serving_size_g"] = {"value": target_value, "source": source_value}
                    changed = True
                current_source = attrs.get("serving_size_g_source", {}).get("value") if isinstance(attrs.get("serving_size_g_source"), dict) else attrs.get("serving_size_g_source")
                if source_value and current_source != source_value:
                    attrs["serving_size_g_source"] = {"value": source_value}
                    changed = True
                ing.attributes = attrs

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


