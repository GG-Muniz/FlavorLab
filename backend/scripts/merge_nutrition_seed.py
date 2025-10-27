#!/usr/bin/env python3
"""
Merge nutrition results (out.json) into scripts/nutrition_seed.json.

- Merges by slug
- Fields considered: calories, protein_g, carbs_g, fat_g, fiber_g, sugars_g
- By default prefers source (out.json) values; can be changed with --prefer seed

Usage:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/merge_nutrition_seed.py --source out.json --dest scripts/nutrition_seed.json --prefer source
"""

import os
import sys
import json
import argparse
from typing import Dict, Any


FIELDS = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugars_g", "serving_size_g", "nutrient_references"]


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f) or {}


def save_json(path: str, obj: Dict[str, Any]) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)


def items_by_slug(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for it in payload.get('items', []) or []:
        slug = (it.get('slug') or '').strip()
        if slug:
            out[slug] = it
    return out


def merge_records(base: Dict[str, Any], incoming: Dict[str, Any], prefer_source: bool) -> Dict[str, Any]:
    res = dict(base)
    for k in FIELDS:
        src_val = incoming.get(k)
        dst_val = res.get(k)
        if src_val is None and dst_val is not None:
            continue
        if prefer_source:
            if src_val is not None:
                res[k] = src_val
        else:
            if dst_val is None and src_val is not None:
                res[k] = src_val
    return res


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Path to out.json produced by FDC fetch')
    parser.add_argument('--dest', default='scripts/nutrition_seed.json', help='Path to nutrition_seed.json')
    parser.add_argument('--prefer', choices=['source', 'seed'], default='source', help='Conflict resolution preference')
    parser.add_argument('--only-missing', action='store_true', help='Only add new slugs, never overwrite existing')
    args = parser.parse_args()

    source = load_json(args.source)
    dest = load_json(args.dest)

    src_map = items_by_slug(source)
    dst_map = items_by_slug(dest)

    prefer_source = (args.prefer == 'source') and (not args.only_missing)

    merged_map: Dict[str, Dict[str, Any]] = dict(dst_map)
    for slug, rec in src_map.items():
        if slug not in merged_map:
            merged_map[slug] = { 'slug': slug }
        if args.only_missing and slug in dst_map:
            continue
        merged_map[slug] = merge_records(merged_map[slug], rec, prefer_source)

    merged_items = [merged_map[k] for k in sorted(merged_map.keys())]
    merged = {
        'metadata': {
            'unit': 'per_100g',
            'source': 'seed+fdc_merge'
        },
        'items': merged_items
    }

    save_json(args.dest, merged)
    print(f"Merged {len(src_map)} items into {args.dest}; total {len(merged_items)} records")


if __name__ == '__main__':
    main()


