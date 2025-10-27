#!/usr/bin/env python3
"""
Delete Cloudinary images NOT in a keep-list under a given folder.

Requires env:
  CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

Usage:
  cd FlavorLab/backend
  ./venv/Scripts/python.exe scripts/cloudinary_cleanup_keep.py --folder healthlab/ingredients --keep-file scripts/keep_public_ids.txt --dry-run
  ./venv/Scripts/python.exe scripts/cloudinary_cleanup_keep.py --folder healthlab/ingredients --keep-file scripts/keep_public_ids.txt
"""

import os
import sys
import argparse
import requests
from typing import List, Set


def read_keep_list(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    keep: Set[str] = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            keep.add(line)
    return keep


def list_resources(cloud: str, api_key: str, api_secret: str, folder: str) -> List[str]:
    auth = (api_key, api_secret)
    url = f"https://api.cloudinary.com/v1_1/{cloud}/resources/image/upload"
    params = { 'prefix': folder + '/', 'max_results': 500 }
    public_ids: List[str] = []
    while True:
        r = requests.get(url, params=params, auth=auth, timeout=20)
        r.raise_for_status()
        data = r.json() or {}
        for res in data.get('resources', []) or []:
            pid = res.get('public_id')
            if pid:
                public_ids.append(pid)
        cursor = data.get('next_cursor')
        if not cursor:
            break
        params['next_cursor'] = cursor
    return public_ids


def delete_resources(cloud: str, api_key: str, api_secret: str, public_ids: List[str]) -> None:
    if not public_ids:
        return
    auth = (api_key, api_secret)
    url = f"https://api.cloudinary.com/v1_1/{cloud}/resources/image/upload"
    # Batch delete in chunks (Cloudinary supports up to ~100 public_ids per request)
    CHUNK = 100
    for i in range(0, len(public_ids), CHUNK):
        chunk = public_ids[i:i+CHUNK]
        r = requests.delete(url, params={'public_ids[]': chunk}, auth=auth, timeout=20)
        r.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', required=True)
    parser.add_argument('--keep-file', required=True, help='Text file with one public_id per line to keep')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    cloud = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key = os.environ.get('CLOUDINARY_API_KEY', '').strip()
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()
    if not cloud or not api_key or not api_secret:
        print('Missing Cloudinary credentials in env (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)')
        sys.exit(1)

    keep = read_keep_list(args.keep_file)
    all_pids = list_resources(cloud, api_key, api_secret, args.folder)
    to_delete = [pid for pid in all_pids if pid not in keep]

    print(f"Found {len(all_pids)} resources in {args.folder}; keeping {len(keep)}; deleting {len(to_delete)}")
    if args.dry_run:
        for pid in to_delete[:50]:
            print(f"would delete: {pid}")
        if len(to_delete) > 50:
            print("… (truncated)")
        return

    if to_delete:
        delete_resources(cloud, api_key, api_secret, to_delete)
        print("Deleted.")
    else:
        print("Nothing to delete.")


if __name__ == '__main__':
    main()


