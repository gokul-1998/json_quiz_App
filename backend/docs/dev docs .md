- to create a new db migration
	- `alembic revision --autogenerate -m "Your migration message"`
- to apply the migration
	- `alembic upgrade head`

- to run pytest
	- `pytest -vx `
- to generate an html coverage report
	- `pytest --cov --cov-report=html`
