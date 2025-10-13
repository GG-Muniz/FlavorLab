# FlavorLab Scripts

This directory contains utility scripts for FlavorLab backend development and maintenance.

## Scripts Overview

### 1. `generate_enriched_ingredients_data.py`
**Purpose**: Enrich ingredients with health pillar mappings

**What it does**:
- Loads `entities.json` (162 entities)
- Maps ingredient names to health pillar IDs using `health_pillars.py`
- Handles old format migration: `{"value": [...]}` → new list format
- Infers health outcomes from ingredient names when possible
- Outputs to `health_pillar_ingredients_enriched.json`

**Usage**:
```bash
cd /home/holberton/FlavorLab/backend
source venv/bin/activate
python scripts/generate_enriched_ingredients_data.py
```

**Output**: `health_pillar_ingredients_enriched.json` with enriched data

---

### 2. `find_unmatched_ingredients.py`
**Purpose**: Diagnostic tool to identify ingredients without health pillar mappings

**What it does**:
- Compares `entities.json` with `health_pillar_ingredients_enriched.json`
- Identifies ingredients without health outcomes
- Groups results by classification (ingredient/nutrient/compound)
- Provides enrichment statistics

**Usage**:
```bash
cd /home/holberton/FlavorLab/backend
source venv/bin/activate
python scripts/find_unmatched_ingredients.py
```

**Output**: Console report showing unmatched ingredients

---

### 3. `seed_database.py`
**Purpose**: Populate database with enriched ingredient data

**⚠️ WARNING**: This script is **DESTRUCTIVE** - it deletes all existing ingredient data

**What it does**:
- Clears all existing Entity and IngredientEntity records
- Loads `health_pillar_ingredients_enriched.json`
- Creates database records with proper model inheritance
- Commits all changes with transaction safety

**Usage**:
```bash
cd /home/holberton/FlavorLab/backend
source venv/bin/activate
python scripts/seed_database.py
```

**Results**:
- 162 total entities seeded
- 69 ingredients (with health pillar data)
- 93 other entities (nutrients + compounds)

---

## Typical Workflow

1. **Initial Setup**:
   ```bash
   # Generate enriched data
   python scripts/generate_enriched_ingredients_data.py
   
   # Check coverage
   python scripts/find_unmatched_ingredients.py
   ```

2. **Improve Coverage** (if needed):
   - Edit `app/models/health_pillars.py`
   - Add new mappings to `OUTCOME_TO_PILLARS` dictionary
   - Re-run enrichment script
   - Verify with diagnostic script

3. **Populate Database**:
   ```bash
   # Seed the database
   python scripts/seed_database.py
   ```

4. **Verify**:
   ```bash
   # Test API endpoints
   curl http://127.0.0.1:8000/api/v1/entities/ingredients
   curl 'http://127.0.0.1:8000/api/v1/entities/ingredients?health_pillars=8'
   ```

---

## Current Stats

- **Total entities**: 162
- **Enriched ingredients**: 70/70 food ingredients (100%)
- **Health pillars**: 8 (IDs 1-8)
- **Enrichment rate**: 43.2% overall (70/162)

**Breakdown**:
- 69 ingredients (100% with health data) ✅
- 68 compounds (not critical for meal planning)
- 25 nutrients (not critical for meal planning)

---

## Health Pillar Reference

| ID | Pillar Name | Description |
|----|-------------|-------------|
| 1 | Increased Energy | Sustained energy and reduced fatigue |
| 2 | Improved Digestion | Healthy digestive function and gut health |
| 3 | Enhanced Immunity | Immune support and resilience |
| 4 | Better Sleep | Quality sleep and rest |
| 5 | Mental Clarity | Focus, cognitive function, and brain health |
| 6 | Heart Health | Cardiovascular health and circulation |
| 7 | Muscle Recovery | Muscle recovery, strength, and athletic performance |
| 8 | Inflammation Reduction | Anti-inflammatory processes |

---

## Troubleshooting

### Script fails with "File not found"
- Ensure you're running from the `backend/` directory
- Check that required JSON files exist

### Database seeding fails
- Verify database tables exist (run migrations first)
- Check SQLAlchemy logs for constraint violations
- Ensure virtual environment is activated

### Low enrichment rate
- Add more mappings to `app/models/health_pillars.py`
- Focus on food ingredients (not compounds/nutrients)
- Re-run enrichment script after changes

---

## Files Generated

- `health_pillar_ingredients_enriched.json` - Enriched ingredient data
- `flavorlab.db` - SQLite database (after seeding)

---

Last updated: 2025-10-13
