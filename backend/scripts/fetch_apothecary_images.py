"""
Fetch images for Apothecary remedies via Unsplash and upload to Cloudinary.

Usage (from repo root):
  venv/Scripts/python.exe FlavorLab/backend/scripts/fetch_apothecary_images.py --force

Env needed (already supported in app.config):
  UNSPLASH_ACCESS_KEY
  CLOUDINARY_CLOUD_NAME
  CLOUDINARY_UPLOAD_PRESET (unsigned)
  CLOUDINARY_FOLDER (optional; default flavorlab/ingredients used as base)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import hashlib
from typing import Any, Dict

import requests
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_JSON = os.path.join(ROOT, "frontend", "src", "static", "apothecary.json")


def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in {" ", "-", "_"}:
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def get_settings_from_env() -> Dict[str, Any]:
    # Load backend/.env if available so you don't need to export vars in shell
    base_backend = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_file = os.path.join(base_backend, ".env")
    if load_dotenv and os.path.exists(env_file):
        load_dotenv(env_file)
    # Read directly from env; mirrors backend settings
    return {
        "unsplash": os.getenv("UNSPLASH_ACCESS_KEY"),
        "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "upload_preset": os.getenv("CLOUDINARY_UPLOAD_PRESET"),
        "folder": os.getenv("CLOUDINARY_FOLDER", "flavorlab/apothecary"),
    }

KEYWORDS_MAP = {
    # Curated keywords per remedy for best visual relevance
    "matcha-green-energy-shot": "matcha green tea energy shot",
    "ginger-mint-digestive-tea": "ginger mint tea digestive",
    "golden-immunity-shot": "turmeric ginger lemon wellness shot",
    "chamomile-sleep-elixir": "chamomile lavender bedtime tea",
    "brain-boost-smoothie": "blueberry walnut smoothie",
    "cardio-support-salad": "salmon salad leafy greens walnuts",
    "recovery-power-shake": "cherry yogurt banana shake",
    "anti-inflammatory-golden-milk": "turmeric golden milk almond milk",
}


def search_unsplash(access_key: str, query: str) -> str | None:
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {"query": query, "orientation": "landscape", "per_page": 1}
        headers = {"Authorization": f"Client-ID {access_key}"}
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        if resp.status_code != 200:
            print(f"[unsplash] search failed {resp.status_code} for query='{query}'")
            return None
        data = resp.json() or {}
        results = data.get("results") or []
        if not results:
            print(f"[unsplash] no results for query='{query}'")
            return None
        # Prefer 'regular' for smaller payloads
        return results[0].get("urls", {}).get("regular")
    except Exception:
        print(f"[unsplash] exception for query='{query}'", file=sys.stderr)
        return None


def upload_cloudinary_from_url(cloud_name: str, upload_preset: str, image_url: str, public_id: str) -> str | None:
    """Upload by remote URL using Cloudinary unsigned preset.

    Important: for remote fetch, the 'file' value must be sent as a normal
    form field (not multipart file). Cloudinary will fetch the URL directly.
    """
    try:
        endpoint = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        # Unsigned upload: Cloudinary only accepts upload_preset, callback, public_id (optional) and file
        data = {
            "upload_preset": upload_preset,
            "file": image_url,
        }
        if public_id:
            data["public_id"] = public_id
        resp = requests.post(endpoint, data=data, timeout=30)
        if resp.status_code not in (200, 201):
            print(f"[cloudinary] upload failed {resp.status_code} pid='{public_id}' url='{image_url}' -> {resp.text[:120]}")
            return None
        out = resp.json() or {}
        return out.get("secure_url") or out.get("url")
    except Exception:
        print(f"[cloudinary] exception uploading pid='{public_id}'", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Fetch Apothecary images and upload to Cloudinary")
    parser.add_argument("--json", default=DEFAULT_JSON, help="Path to apothecary.json")
    parser.add_argument("--force", action="store_true", help="Overwrite existing image_url values")
    parser.add_argument("--cloud", default=None, help="Cloudinary cloud name (overrides env)")
    parser.add_argument("--preset", default=None, help="Cloudinary unsigned upload preset (overrides env)")
    parser.add_argument("--folder", default=None, help="Cloudinary folder (overrides env)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    cfg = get_settings_from_env()
    access_key = cfg.get("unsplash")
    cloud = args.cloud or cfg.get("cloud_name")
    preset = args.preset or cfg.get("upload_preset")
    folder = args.folder or cfg.get("folder")

    if not os.path.exists(args.json):
        print(f"JSON file not found: {args.json}")
        sys.exit(1)

    if not cloud or not preset:
        print("Cloudinary CLOUDINARY_CLOUD_NAME and CLOUDINARY_UPLOAD_PRESET are required. Set env vars or pass --cloud/--preset.")
        sys.exit(2)

    with open(args.json, "r", encoding="utf-8") as f:
        payload = json.load(f) or {}

    items = payload.get("apothecary_responses") or []
    updated = 0
    for item in items:
        if (item.get("image_url") and not args.force):
            continue
        remedy = item.get("remedy") or ""
        goal = item.get("health_goal") or ""
        rid = slugify(remedy)
        curated = KEYWORDS_MAP.get(rid)
        if curated:
            query = curated
        else:
            # generic fallback
            query = f"{remedy} {goal} healthy wellness food drink"

        # Find an image URL
        if access_key:
            src_url = search_unsplash(access_key, query)
        else:
            src_url = None

        if not src_url:
            # Unsplash source fallback
            q = requests.utils.quote(query)
            src_url = f"https://source.unsplash.com/featured/800x480/?{q}"

        target_url = src_url
        final_public_id = None
        if cloud and preset:
            pid_base = f"{remedy}-{goal}-{src_url}"
            pid = slugify(f"{folder}/" + hashlib.sha1(pid_base.encode("utf-8")).hexdigest()[:12])
            cloud_url = upload_cloudinary_from_url(cloud, preset, src_url, pid)
            if cloud_url:
                target_url = cloud_url
                final_public_id = pid
                if args.verbose:
                    print(f"[ok] {rid} -> {target_url}")
            else:
                if args.verbose:
                    print(f"[warn] cloud upload failed, keeping source URL for {rid}")

        item["image_url"] = target_url
        if final_public_id:
            item["cloudinary_public_id"] = final_public_id
        updated += 1
        time.sleep(0.2)  # gentle pacing

    if updated:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Updated {updated} image_url entries in {args.json}")
    else:
        print("No updates needed (use --force to overwrite)")


if __name__ == "__main__":
    main()


