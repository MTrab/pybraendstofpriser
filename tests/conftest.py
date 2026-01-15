"""Fixtures for the pybraendstofpriser test suite."""

import json
from pathlib import Path
import pytest
from pybraendstofpriser import Braendstofpriser


@pytest.fixture
def api():
    """Provide an instance of the Braendstofpriser API client."""
    return Braendstofpriser()


@pytest.fixture
def load_fixture():
    """
    Load data from the fixtures directory.

    Returns:
        - dict/list: If the file is a .json file.
        - bytes: If the file is an .xls or .xlsx file (Excel).
        - str: For all other file types (HTML, text).
    """

    def _load(filename):
        # Locate the file in the fixtures subdirectory
        fixture_path = Path(__file__).parent / "fixtures" / filename

        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

        # Handle binary Excel files
        if filename.endswith((".xls", ".xlsx")):
            return fixture_path.read_bytes()

        # Handle text-based files
        content = fixture_path.read_text(encoding="utf-8")
        if filename.endswith(".json"):
            return json.loads(content)

        return content

    return _load
