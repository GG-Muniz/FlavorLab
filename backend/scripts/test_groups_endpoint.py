#!/usr/bin/env python3
"""Quick smoke test for GET /entities/ingredients/groups."""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from app.main import app
from fastapi.testclient import TestClient


def main() -> None:
    client = TestClient(app)
    res = client.get("/entities/ingredients/groups", params={"size_per_group": 5})
    print("status:", res.status_code)
    data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
    groups = data.get("groups", []) if isinstance(data, dict) else []
    print("groups:", len(groups))
    if groups:
        g = groups[0]
        print("first_group:", g.get("category_slug"), "items:", len(g.get("items") or []))


if __name__ == "__main__":
    main()


