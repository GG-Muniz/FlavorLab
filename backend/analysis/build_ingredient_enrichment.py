"""Generate enriched ingredient descriptions combining compounds and vitamin/mineral data.

Usage:
    cd FlavorLab/backend
    ./venv/Scripts/python.exe analysis/build_ingredient_enrichment.py

Outputs:
    analysis/ingredient_enrichment.json
    analysis/ingredient_enrichment_report.json
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR.parent / "flavorlab.db"
COMPOUND_DETAILS_PATH = BASE_DIR / "compound_details.json"
VITAMIN_DETAILS_PATH = BASE_DIR / "vitamin_mineral_details.json"


@dataclass
class CompoundDetail:
    name: str
    summary: str
    primary_actions: List[str]
    evidence_level: str


@dataclass
class VitaminDetail:
    name: str
    summary: str
    primary_actions: List[str]
    evidence_level: str
    amount_reference: Optional[str] = None


def _load_compound_details() -> Dict[str, CompoundDetail]:
    data = json.loads(COMPOUND_DETAILS_PATH.read_text(encoding="utf-8"))
    return {
        entry["name"]: CompoundDetail(
            name=entry["name"],
            summary=entry["summary"],
            primary_actions=list(entry.get("primary_actions", [])),
            evidence_level=entry.get("evidence_level", "Emerging"),
        )
        for entry in data
    }


def _load_vitamin_details() -> Dict[str, VitaminDetail]:
    data = json.loads(VITAMIN_DETAILS_PATH.read_text(encoding="utf-8"))
    details: Dict[str, VitaminDetail] = {}
    for entry in data:
        details[entry["name"]] = VitaminDetail(
            name=entry["name"],
            summary=entry["summary"],
            primary_actions=list(entry.get("primary_actions", [])),
            evidence_level=entry.get("evidence_level", "Established"),
            amount_reference=entry.get("amount_reference"),
        )
    return details


def _load_ingredients() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, attributes
        FROM entities
        WHERE primary_classification = 'ingredient'
        ORDER BY name
        """
    )
    rows = cur.fetchall()
    conn.close()

    ingredients: List[Dict[str, Any]] = []
    for row in rows:
        attrs = json.loads(row["attributes"] or "{}")
        ingredients.append(
            {
                "id": row["id"],
                "name": row["name"],
                "attributes": attrs,
            }
        )
    return ingredients


def _extract_key_compounds(attrs: Dict[str, Any]) -> List[str]:
    raw = attrs.get("key_compounds")
    values: Iterable[str]
    if isinstance(raw, dict):
        values = raw.get("value") or []
    elif isinstance(raw, list):
        values = raw
    else:
        values = []
    return [str(v).strip() for v in values if str(v).strip()]


def _extract_compound_concentrations(attrs: Dict[str, Any]) -> Dict[str, str]:
    raw = attrs.get("compound_concentrations")
    mapping: Dict[str, str] = {}
    if isinstance(raw, dict):
        value = raw.get("value") if "value" in raw else raw
        if isinstance(value, dict):
            for k, v in value.items():
                if k:
                    mapping[str(k).strip()] = str(v).strip()
    return mapping


def _extract_vitamins(attrs: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = attrs.get("nutrient_references")
    entries: Iterable[Any]
    if isinstance(raw, dict):
        entries = raw.get("value") or []
    elif isinstance(raw, list):
        entries = raw
    else:
        entries = []

    vitamins: List[Dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        name = item.get("nutrient_name") or item.get("name")
        ntype = (item.get("nutrient_type") or "").lower()
        if not name:
            continue
        if any(token in ntype for token in ("vitamin", "mineral", "micronutr")):
            vitamins.append(
                {
                    "name": str(name).strip(),
                    "concentration": str(item.get("concentration") or "").strip(),
                }
            )
    return vitamins


def build() -> None:
    compounds_info = _load_compound_details()
    vitamin_info = _load_vitamin_details()
    ingredients = _load_ingredients()

    enriched_records: List[Dict[str, Any]] = []
    missing_compounds_counter: Counter[str] = Counter()
    missing_vitamins_counter: Counter[str] = Counter()

    for ingredient in ingredients:
        attrs = ingredient["attributes"]
        key_compounds = _extract_key_compounds(attrs)
        compound_concentrations = _extract_compound_concentrations(attrs)
        vitamin_refs = _extract_vitamins(attrs)

        compound_details = []
        missing_compounds = []
        for comp in key_compounds:
            info = compounds_info.get(comp)
            if not info:
                missing_compounds.append(comp)
                missing_compounds_counter[comp] += 1
                continue
            compound_details.append(
                {
                    "name": info.name,
                    "summary": info.summary,
                    "primary_actions": info.primary_actions,
                    "evidence_level": info.evidence_level,
                    "concentration": compound_concentrations.get(info.name, ""),
                }
            )

        vitamin_details = []
        missing_vitamins = []
        seen_vitamin_names = set()
        for ref in vitamin_refs:
            name = ref["name"]
            if name in seen_vitamin_names:
                continue
            seen_vitamin_names.add(name)
            info = vitamin_info.get(name)
            if not info:
                missing_vitamins.append(name)
                missing_vitamins_counter[name] += 1
                continue
            vitamin_details.append(
                {
                    "name": info.name,
                    "summary": info.summary,
                    "primary_actions": info.primary_actions,
                    "evidence_level": info.evidence_level,
                    "amount_reference": info.amount_reference,
                    "amount_per_100g": ref.get("concentration", ""),
                }
            )

        enriched_records.append(
            {
                "id": ingredient["id"],
                "name": ingredient["name"],
                "key_compounds": compound_details,
                "vitamins_minerals": vitamin_details,
                "missing_compounds": missing_compounds,
                "missing_vitamins": missing_vitamins,
            }
        )

    (BASE_DIR / "ingredient_enrichment.json").write_text(
        json.dumps(enriched_records, indent=2),
        encoding="utf-8",
    )

    report = {
        "total_ingredients": len(enriched_records),
        "ingredients_with_compound_gaps": sum(1 for r in enriched_records if r["missing_compounds"]),
        "ingredients_with_vitamin_gaps": sum(1 for r in enriched_records if r["missing_vitamins"]),
        "missing_compound_frequency": sorted(missing_compounds_counter.items(), key=lambda kv: (-kv[1], kv[0])),
        "missing_vitamin_frequency": sorted(missing_vitamins_counter.items(), key=lambda kv: (-kv[1], kv[0])),
    }

    (BASE_DIR / "ingredient_enrichment_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(
        f"Generated ingredient enrichment for {len(enriched_records)} items. "
        f"Compound gaps: {report['ingredients_with_compound_gaps']} | "
        f"Vitamin gaps: {report['ingredients_with_vitamin_gaps']}"
    )


if __name__ == "__main__":
    build()
