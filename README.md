# FlavorLab

FlavorLab is a comprehensive database system for managing and analyzing ingredients, nutrients, and their relationships. It provides tools for scraping nutrient data, processing ingredient information, and organizing this data in a structured format.

## Features

- **Unified Entity Model**: Centralized representation of ingredients, nutrients, and compounds
- **Relationship Management**: Track relationships between entities (contains, found_in, etc.)
- **Flexible Classification**: Multi-level classification system for entities
- **Attribute System**: Extensible attribute storage with source and confidence tracking
- **Query API**: Rich query capabilities for entities and relationships
- **Synonyms & Classes**: Search by synonyms; compound classes modeled explicitly
- **Context & Uncertainty**: Relationship context (state/mechanisms/params) and uncertainty (mean/sd/min/max)
- **Data Migration**: Tools to migrate from legacy formats to the unified model
- **Compatibility Layer**: Adapters for working with legacy data formats

## Directory Structure

```
FlavorLab/
├── config/               # Configuration settings
├── data/                 # Data storage
│   ├── processed/        # Processed data
│   │   ├── entities/     # Unified entity model data
│   │   ├── ingredients/  # Legacy ingredient data
│   │   ├── nutrients/    # Legacy nutrient data
│   │   └── metadata/     # Summary metadata
│   └── raw/              # Raw scraped data
├── scripts/              # Command-line scripts
├── src/                  # Source code
│   ├── api/              # Query and CRUD APIs
│   ├── compatibility/    # Legacy format adapters
│   ├── models/           # Data models
│   ├── processors/       # Data processors
│   ├── scraper/          # Web scraping components
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── api/              # API tests
│   ├── models/           # Model tests
│   ├── processors/       # Processor tests
│   └── utils/            # Utility tests
└── tools/                # Development tools
```

## Getting Started

### Prerequisites

- Python 3.9+
- Chrome browser (for web scraping)
- ChromeDriver (for Selenium)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FlavorLab.git
   cd FlavorLab
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up ChromeDriver:
   - Download ChromeDriver matching your Chrome version
   - Place it in the project root or in chromedriver-win64/chromedriver.exe

### Usage

#### Scraping Nutrients

```bash
python scripts/run_scraper.py
```

#### Processing Ingredients

```bash
python scripts/process_ingredients.py data/ingredients_clean_semicolon.csv
```

#### Migrating to Unified Model

```bash
# Migrate nutrients
python scripts/migrate_nutrients.py

# Migrate ingredients
python scripts/migrate_ingredients.py

# Create relationships
python scripts/create_relationships.py
```

#### Exporting to Legacy Format

```bash
python scripts/export_legacy_format.py --nutrients --ingredients
```

## Data Model

### Entity

The core of the unified model is the `Entity` class, which represents any item in the database:

```python
entity = Entity(
    id="salmon",
    name="Salmon",
    primary_classification="ingredient"
)

# Add classifications
entity.add_classification("fish")
entity.add_classification("protein")

# Add attributes
entity.add_attribute("foodb_priority", "Critical", source="FlavorLab", confidence=5)
entity.add_attribute("health_outcomes", ["Energy", "Inflammation", "Sleep"], confidence=4)
```

### Relationship

Relationships connect entities:

```python
relationship = Relationship(
    source_id="salmon",
    relationship_type="contains",
    target_id="omega_3",
    quantity="1.2",
    unit="g/100g",
    confidence_score=5,
    context={"state": "raw", "mechanisms": [], "params": {}},
    uncertainty={"mean": 1.2, "sd": 0.1}
)
```
### New utilities & scripts

- Unit normalization: `src/utils/unit_normalization.py`
- ND representation: `src/utils/nd.py`
- ID policy utilities: `src/utils/id_policy.py`
- Validate entities/relationships: `scripts/validate_entities.py`
- Migrate IDs and attach external codes: `scripts/migrate_ids.py --mapping mapping.json`
- Import ingredient→compound mappings: `scripts/import_ingredient_compounds.py --input mapping.json`

See `docs/images/` for visual guides and `docs/DENSITIES.md` for conversion references.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.