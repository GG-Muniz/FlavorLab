# FlavorLab Backend MVP

A FastAPI-based backend for the FlavorLab intelligent cooking platform, featuring SQLite database with JSON data migration capabilities.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip (Python package installer)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize the database:**
   ```bash
   python scripts/init_db.py
   ```

### Database Migration

The `scripts/init_db.py` script handles the complete database setup and data migration:

```bash
# Basic migration
python scripts/init_db.py

# Drop existing tables and recreate
python scripts/init_db.py --drop-existing

# Use custom JSON files
python scripts/init_db.py --entities-file custom_entities.json --relationships-file custom_relationships.json
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/              # SQLAlchemy models
│   │   ├── entity.py        # Core Entity model + specialized types
│   │   ├── relationship.py  # RelationshipEntity model
│   │   └── user.py          # User model for authentication
│   ├── database.py          # Database configuration
│   ├── config.py            # Application settings
│   └── main.py              # FastAPI app entry point
├── scripts/
│   └── init_db.py           # Database initialization & migration
├── requirements.txt         # Python dependencies
└── .env.example            # Environment configuration template
```

## 🧪 Testing

Run the full test suite (pytest):
```bash
python -m pytest -q
```

Handy options:
- short tracebacks: `pytest --tb=short`
- show prints: `pytest -s`
- JUnit XML: `pytest --junit-xml=report.xml`

## 🗄️ Database Models

### Entity Model
The core model representing any item in FlavorLab:
- **Base Entity**: Generic entity with flexible attributes
- **IngredientEntity**: Specialized for ingredients with health outcomes
- **NutrientEntity**: Specialized for nutrients with function descriptions
- **CompoundEntity**: Specialized for compounds with molecular data

### RelationshipEntity Model
Manages connections between entities:
- Source and target entity references
- Relationship types (contains, found_in, etc.)
- Quantitative data (quantity, unit)
- Context and uncertainty information
- Confidence scoring

### User Model
Basic authentication model:
- Email/password authentication
- User profile information
- Preferences storage
- Account status tracking

## 🔧 Configuration

The application uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_NAME` | `flavorlab.db` | SQLite database filename |
| `DEBUG` | `false` | Enable debug mode |
| `SECRET_KEY` | `your-secret-key...` | JWT secret key |
| `BATCH_SIZE` | `100` | Batch size for data migration |

## 📊 Data Migration

The migration script processes JSON files with the following structure:

### Entities JSON
```json
{
  "metadata": {
    "total_entities": 162,
    "primary_classifications": {
      "nutrient": 25,
      "ingredient": 69,
      "compound": 68
    }
  },
  "entities": [
    {
      "id": 1,
      "name": "Fat",
      "primary_classification": "nutrient",
      "classifications": ["macronutrients"],
      "attributes": {
        "nutrient_type": {
          "value": "macronutrients",
          "source": null,
          "confidence": null
        }
      }
    }
  ]
}
```

### Relationships JSON
```json
{
  "metadata": {
    "total_relationships": 515,
    "relationship_types": {
      "contains": 321,
      "found_in": 194
    }
  },
  "relationships": [
    {
      "source_id": "garlic",
      "relationship_type": "contains",
      "target_id": 1,
      "quantity": "variable",
      "unit": null,
      "context": {},
      "uncertainty": {},
      "confidence_score": 3
    }
  ]
}
```

## 📦 Requirements

Dependencies are pinned in `requirements.txt`. To (re)generate from your venv:
```bash
pip freeze > requirements.txt
```

## 🚀 Running the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📝 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔍 Database Queries

Example queries using the models:

```python
from app.database import SessionLocal
from app.models import Entity, RelationshipEntity

# Get all ingredients
db = SessionLocal()
ingredients = db.query(Entity).filter(Entity.primary_classification == "ingredient").all()

# Find relationships for an entity
relationships = db.query(RelationshipEntity).filter(
    RelationshipEntity.source_id == "garlic"
).all()

# Get entities with specific classifications
nutrients = db.query(Entity).filter(
    Entity.classifications.contains(["macronutrients"])
).all()
```

## 🛠️ Development

### Adding New Models
1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Update `app/database.py` imports
4. Run migration script

### Database Schema Changes
1. Modify models
2. Run `python scripts/init_db.py --drop-existing`
3. Test with sample data

## ✅ Current Status

- All tests passing locally: 187 passed, 2 warnings (pytest)
- Pydantic v2 migration completed (`model_validate` used, no `from_orm`)
- Datetime updated to timezone-aware `datetime.now(UTC)`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
