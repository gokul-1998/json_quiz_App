# Backend Tests

This directory contains tests for the backend API.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_routers/` - Tests for API routers
  - `test_auth.py` - Tests for authentication endpoints
  - `test_decks.py` - Tests for deck management endpoints
- `test_auth_utils.py` - Tests for authentication utility functions
- `test_models.py` - Tests for database models
- `test_middleware.py` - Tests for middleware components

## Running Tests

To run the tests, use the following command from the backend directory:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing
```

## Test Coverage

The project is configured to require at least 80% test coverage. You can adjust this requirement in `pytest.ini`.

## Writing New Tests

When adding new tests:

1. Place router tests in the appropriate file in `test_routers/`
2. Use fixtures from `conftest.py` when possible
3. Mock external dependencies
4. Test both success and failure cases
5. Follow the existing naming conventions