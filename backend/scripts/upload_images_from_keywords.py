#!/usr/bin/env python3
"""
Download representative images from Unsplash Source for curated keywords,
upload to Cloudinary (unsigned preset recommended), and set stable
cloudinary delivery URLs on ingredients.

Prereqs:
  - CLOUDINARY_CLOUD_NAME set
  - Either CLOUDINARY_UPLOAD_PRESET (unsigned) OR API key/secret for signed
  - image_keywords.json provides good keywords for top ingredients

Run:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/upload_images_from_keywords.py
"""

import os
import sys
import io
import json
import time
from typing import Dict
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

import requests
from app.database import SessionLocal, Base, engine
from app.models.entity import IngredientEntity
from app.config import get_settings


def load_keywords() -> Dict[str, str]:
    path = os.path.join(script_dir, 'image_keywords.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f) or {}


def fetch_unsplash_bytes(query: str, access_key: str | None) -> bytes:
    # Try API twice, then Source twice
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            if access_key:
                search_url = 'https://api.unsplash.com/search/photos'
                params = { 'query': query, 'per_page': 1, 'orientation': 'landscape' }
                headers = { 'Authorization': f'Client-ID {access_key}', 'Accept-Version': 'v1' }
                r = requests.get(search_url, params=params, headers=headers, timeout=12)
                r.raise_for_status()
                data = r.json()
                results = (data or {}).get('results', [])
                if results:
                    img_url = results[0]['urls']['regular']
                    img = requests.get(img_url, timeout=12)
                    img.raise_for_status()
                    return img.content
            break
        except Exception as e:
            last_err = e
            time.sleep(1.0 + attempt)
    for attempt in range(2):
        try:
            url = f'https://source.unsplash.com/featured/?{query}'
            r = requests.get(url, timeout=12)
            r.raise_for_status()
            return r.content
        except Exception as e:
            last_err = e
            time.sleep(1.0 + attempt)
    raise last_err or RuntimeError('Failed to fetch Unsplash image')


def upload_to_cloudinary(cloud_name: str, preset: str, file_bytes: bytes, public_id: str) -> str:
    url = f'https://api.cloudinary.com/v1_1/{cloud_name}/image/upload'
    data = {'upload_preset': preset, 'public_id': public_id}
    files = {'file': ('image.jpg', io.BytesIO(file_bytes), 'image/jpeg')}
    r = requests.post(url, data=data, files=files, timeout=20)
    r.raise_for_status()
    j = r.json()
    # Prefer secure_url
    return j.get('secure_url') or j.get('url')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0, help='Process at most N ingredients')
    parser.add_argument('--only-missing', action='store_true', help='Skip items that already have Cloudinary URLs')
    parser.add_argument('--verbose', action='store_true', help='Print progress per item')
    parser.add_argument('--slugs', type=str, default='', help='Comma-separated slugs to process (only these)')
    parser.add_argument('--force', action='store_true', help='Re-upload even if image_url is already set')
    parser.add_argument('--replace', action='store_true', help='Use a new public_id (slug-timestamp) to force a new asset')
    args = parser.parse_args()
    settings = get_settings()
    cloud = (settings.cloudinary_cloud_name or '').strip()
    preset = (settings.cloudinary_upload_preset or '').strip()
    folder = (getattr(settings, 'cloudinary_folder', '') or 'flavorlab/ingredients').strip('/')
    unsplash_key = (getattr(settings, 'unsplash_access_key', None) or '').strip() or None
    if not cloud or not preset:
        print('CLOUDINARY_CLOUD_NAME and CLOUDINARY_UPLOAD_PRESET required for this script')
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    keywords = load_keywords()
    db = SessionLocal()
    uploaded = 0
    try:
        items = db.query(IngredientEntity).all()
        wanted = set(s.strip() for s in (args.slugs or '').split(',') if s.strip())
        total = len(items)
        count = 0
        for idx, ing in enumerate(items, 1):
            slug = (getattr(ing, 'slug', None) or '').strip()
            if not slug:
                continue
            if wanted and slug not in wanted:
                continue
            if args.limit and count >= args.limit:
                break
            if args.only_missing and not args.force:
                url = getattr(ing, 'image_url', '') or ''
                if url.startswith('https://res.cloudinary.com/'):
                    continue
            query = keywords.get(slug)
            if not query:
                # fallback: broaden
                query = slug.replace('-', ',')
            try:
                if args.verbose:
                    print(f"[{idx}/{total}] {slug} ← {query}")
                img_bytes = fetch_unsplash_bytes(query, unsplash_key)
                if args.replace:
                    public_id = f"{folder}/{slug}-{int(time.time())}"
                else:
                    public_id = f"{folder}/{slug}"
                url = upload_to_cloudinary(cloud, preset, img_bytes, public_id)
                if url and getattr(ing, 'image_url', None) != url:
                    ing.image_url = url
                    uploaded += 1
                    count += 1
                    # be nice to APIs
                    time.sleep(0.4)
            except Exception as e:
                print(f"skip {slug}: {e}")
                continue
        if uploaded:
            db.commit()
        print(f"Uploaded and set image_url for {uploaded} ingredients")
    finally:
        db.close()


if __name__ == '__main__':
    main()


