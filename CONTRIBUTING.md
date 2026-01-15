## Contributing to pybraendstofpriser

Thank you for your interest in contributing! To maintain a high-quality codebase, we use a data-driven testing approach. Please follow these guidelines when adding new features or companies.

## Development Workflow

Fork the repository and create your branch from `main`.

Install dependencies using `poetry install`.

Ensure all existing tests pass: `poetry run pytest -v -m "not live"`.

## Adding a New Fuel Company

When adding a new fuel company, you must provide a data fixture (a "dump") of the raw source data. This allows us to test the parsing logic without relying on external websites during CI/CD.

### 1\. Implement the Scraper

Create the new company module in `pybraendstofpriser/companies/`. Ensure it uses the existing tools in `pybraendstofpriser/tools.py` for network requests.

### 2\. Update the Dump Script

You must add the new company's data source to `scripts/dump_fixtures.py`.

Add a new entry to the `DUMP_CONFIG` list.

Specify the filename (e.g., `new_company.json`), the URL, and the type (`json`, `xls`, or `html`).

### 3\. Generate the Fixture

Before submitting a Pull Request, run the dump script to generate the necessary files:

Bash

```plaintext
poetry run python scripts/dump_fixtures.py
Verify that the new file appears in tests/fixtures/.
```

### 4\. Add Tests

Add the new company details to the `COMPANIES_DATA` list in `tests/test_api.py`. This automatically enables:

**Offline testing**: Verifies your parser against the fixture you just created.

**Live testing**: Verifies the actual website connectivity.

## Testing Requirements

**No Network in Unit Tests**: Unit tests must never make actual network calls. Always use the `load_fixture` and `mocker` patterns established in the test suite.

**English Documentation**: All docstrings, comments, and log messages in tests must be in English.

**Verbose Output**: Use `pytest -v` to ensure test IDs (company names) are clearly visible in logs.

## Pull Request Process

Ensure your branch passes the CI workflow (the offline tests).

Update the `README.md` if your changes introduce new configuration options.

Describe your changes clearly in the PR description, noting if any fixtures were refreshed.