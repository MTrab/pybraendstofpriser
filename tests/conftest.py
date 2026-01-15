import json
import pandas as pd
from pathlib import Path
import pytest
from pybraendstofpriser import Braendstofpriser


@pytest.fixture
def api():
    """Standard initialization of the API client."""
    return Braendstofpriser()


@pytest.fixture
def load_fixture():
    def _load(filename):
        fixture_path = Path(__file__).parent / "fixtures" / filename

        if not fixture_path.exists():
            for ext in [".csv", ".xlsx", ".xls", ".html"]:
                alt_path = fixture_path.with_suffix(ext)
                if alt_path.exists():
                    fixture_path = alt_path
                    break
            else:
                raise FileNotFoundError(f"Fixture {filename} not found.")

        # 1. Handle JSON/HTML/Text
        if fixture_path.suffix == ".json":
            return json.loads(fixture_path.read_text(encoding="utf-8"))
        if fixture_path.suffix == ".html" or "goon" in filename:
            return fixture_path.read_text(encoding="utf-8")

        content = fixture_path.read_bytes()

        # 2. Try Excel Parsing
        if fixture_path.suffix in [".xlsx", ".xls"]:
            return pd.read_excel(fixture_path)

        raise ValueError(
            f"Failed to parse {filename}. The file format or headers are unrecognized."
        )

    return _load
