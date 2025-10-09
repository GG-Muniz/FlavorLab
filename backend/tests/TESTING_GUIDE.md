# FlavorLab Backend Testing Guide

## 🧪 Comprehensive Test Suite Overview

The FlavorLab backend MVP includes a comprehensive test suite designed to validate every component of the system. This guide provides detailed information about the test structure, how to run tests, and what each test category covers.

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_api/                # API endpoint tests
│   ├── test_auth.py         # Authentication and JWT tests
│   ├── test_users.py        # User management tests
│   ├── test_entities.py     # Entity CRUD and search tests
│   ├── test_relationships.py # Relationship management tests
│   ├── test_health.py       # Health API tests
│   └── test_flavor.py       # Flavor API tests
├── test_services/           # Business logic tests
│   ├── test_search_service.py # Search and filtering tests
│   ├── test_auth_service.py   # Authentication service tests
│   └── test_matcher_service.py # Matching algorithm tests
├── test_models/             # SQLAlchemy model tests
│   ├── test_entity_model.py    # Entity model tests
│   ├── test_relationship_model.py # Relationship model tests
│   └── test_user_model.py      # User model tests
├── test_scripts/            # Utility script tests
│   └── test_init_db.py      # Database initialization tests
└── fixtures/                # Test data fixtures
    ├── test_entities.json   # Sample entity data
    └── test_relationships.json # Sample relationship data
```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py --coverage

# Run specific test category
python run_tests.py --category models

# Run with verbose output
python run_tests.py --verbose
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_api/test_auth.py::TestUserRegistration::test_register_user_success
```

## 🧩 Test Categories

### 1. **Model Tests** (`test_models/`)

Tests the SQLAlchemy models and their functionality:

- **Entity Model Tests**:
  - Model creation and validation
  - Attribute management
  - Classification handling
  - Type checking methods
  - Relationship connections

- **Relationship Model Tests**:
  - Relationship creation and validation
  - Context and uncertainty management
  - Confidence scoring
  - Foreign key constraints

- **User Model Tests**:
  - User creation and validation
  - Authentication status
  - Profile management
  - Preferences handling

### 2. **API Tests** (`test_api/`)

Tests all REST API endpoints:

- **Authentication Tests**:
  - User registration (success, duplicates, validation)
  - User login (success, failures, JWT generation)
  - Token validation and usage
  - Complete authentication flow

- **User Management Tests**:
  - Profile retrieval and updates
  - Password changes
  - Account deactivation
  - User statistics
  - Admin operations

- **Entity API Tests**:
  - Entity listing with pagination and filtering
  - Entity search with complex criteria
  - Entity CRUD operations
  - Entity connections and relationships
  - Statistics and suggestions

- **Relationship API Tests**:
  - Relationship listing and filtering
  - Relationship search
  - Relationship CRUD operations
  - Entity relationship queries

- **Health API Tests**:
  - Health outcomes listing
  - Health recommendations
  - User health goals
  - Health statistics

- **Flavor API Tests**:
  - Flavor profile management
  - Flavor recommendations
  - Popular combinations
  - Flavor statistics

### 3. **Service Tests** (`test_services/`)

Tests business logic and core services:

- **Search Service Tests**:
  - Entity search with various filters
  - Relationship search and filtering
  - Entity connection analysis
  - Relationship path finding
  - Statistics generation
  - Search suggestions

- **Authentication Service Tests**:
  - Password hashing and verification
  - JWT token creation and validation
  - User authentication
  - Session management

### 4. **Script Tests** (`test_scripts/`)

Tests utility scripts and data migration:

- **Database Initialization Tests**:
  - Table creation and schema validation
  - JSON data loading and parsing
  - Entity migration with batch processing
  - Relationship migration
  - Data integrity validation
  - Error handling and recovery

## 🔧 Test Fixtures

### Database Fixtures

- **`db_session`**: Isolated database session for each test
- **`client`**: FastAPI test client with database override
- **`authenticated_client`**: Pre-authenticated test client
- **`admin_client`**: Admin-level authenticated client

### Data Fixtures

- **`test_user`**: Sample user for testing
- **`admin_user`**: Admin user for testing
- **`sample_entity`**: Sample entity for testing
- **`sample_relationship`**: Sample relationship for testing
- **`multiple_entities`**: Multiple entities for search testing

### Utility Fixtures

- **`temp_json_file`**: Temporary JSON file for migration testing
- **`test_user_data`**: User registration data
- **`sample_entity_data`**: Entity creation data

## 📊 Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ **All API endpoints** (100% coverage)
- ✅ **All model methods** (100% coverage)
- ✅ **All service functions** (100% coverage)
- ✅ **Error handling paths** (90%+ coverage)
- ✅ **Authentication flows** (100% coverage)
- ✅ **Data validation** (100% coverage)

## 🎯 Test Scenarios

### Happy Path Tests

- Successful user registration and login
- Entity creation, retrieval, and updates
- Relationship management
- Search and filtering operations
- Authentication and authorization

### Error Handling Tests

- Invalid input validation
- Authentication failures
- Authorization errors
- Database constraint violations
- Network and connection errors

### Edge Case Tests

- Empty search results
- Pagination boundaries
- Large dataset handling
- Concurrent operations
- Data migration edge cases

### Integration Tests

- Complete user workflows
- API endpoint integration
- Database transaction handling
- Authentication flow integration
- Search and recommendation integration

## 🔍 Test Data

### Sample Entities

- **Turmeric**: Ingredient with anti-inflammatory properties
- **Ginger**: Ingredient with digestive health benefits
- **Vitamin C**: Nutrient with immune system support

### Sample Relationships

- **Contains relationships**: Entity-to-compound connections
- **Found in relationships**: Compound-to-entity connections
- **Context data**: State, mechanisms, and parameters
- **Uncertainty data**: Statistical measures and confidence

### Sample Users

- **Test User**: Regular user with full profile
- **Admin User**: Administrative user with elevated privileges
- **Unverified User**: User pending verification

## 🚨 Common Test Issues

### Database Isolation

Each test runs with a fresh database to ensure isolation:

```python
@pytest.fixture(scope="function")
def db_session():
    # Creates fresh in-memory database for each test
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

### Authentication Testing

Tests use pre-authenticated clients to avoid repetitive login:

```python
@pytest.fixture
def authenticated_client(client, test_user_token):
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client
```

### Data Cleanup

Tests automatically clean up temporary files and database changes:

```python
@pytest.fixture(autouse=True)
def cleanup_temp_files(temp_json_file):
    yield
    try:
        if os.path.exists(temp_json_file):
            os.unlink(temp_json_file)
    except Exception:
        pass
```

## 📈 Performance Testing

### Load Testing

- Batch entity creation (100+ entities)
- Large search result sets (1000+ results)
- Concurrent user operations
- Database migration performance

### Memory Testing

- Large JSON file processing
- Memory usage during batch operations
- Garbage collection verification

## 🔧 Debugging Tests

### Running Individual Tests

```bash
# Run specific test method
pytest tests/test_api/test_auth.py::TestUserRegistration::test_register_user_success -v

# Run with debugging
pytest tests/test_api/test_auth.py -v -s --pdb

# Run with detailed output
pytest tests/test_api/test_auth.py -v -s --tb=long
```

### Test Debugging Tips

1. **Use `-s` flag** to see print statements
2. **Use `--pdb` flag** to drop into debugger on failure
3. **Use `--tb=long`** for detailed tracebacks
4. **Check database state** in `db_session` fixture
5. **Verify authentication** in `authenticated_client` fixture

## 📋 Test Checklist

Before running tests, ensure:

- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] Database is properly configured
- [ ] Test environment variables are set
- [ ] No conflicting processes are running
- [ ] Sufficient disk space for test data

## 🎉 Test Results

### Successful Test Run

```
FlavorLab Test Suite
==================================================
✅ All tests passed!

📊 Coverage report generated:
   - HTML report: htmlcov/index.html
   - Terminal report: See output above

🚀 Test suite completed successfully!
```

### Failed Test Run

```
FlavorLab Test Suite
==================================================
❌ Some tests failed!

Detailed output:
[Test failure details]

💥 Test suite failed!
```

## 🔄 Continuous Integration

The test suite is designed to work with CI/CD pipelines:

- **GitHub Actions**: Automated testing on push/PR
- **Docker**: Containerized test environment
- **Coverage Reports**: Automated coverage tracking
- **Test Reports**: Detailed test result reporting

## 📚 Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **SQLAlchemy Testing**: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
- **Test Coverage**: https://coverage.readthedocs.io/

---

The FlavorLab test suite provides comprehensive validation of all backend components, ensuring reliability, security, and performance of the intelligent cooking platform.
