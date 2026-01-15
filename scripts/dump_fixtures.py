"""
Download HTML pages from fuel price providers
and store them as test fixtures.

Run manually:
    python scripts/dump_fixtures.py

⚠️ Never run this in CI.
"""

from pathlib import Path
import requests

FIXTURES_DIR = Path("tests/fixtures")
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

SITES = {
    "f24": {
        "url": "https://beta.q8.dk/Station/GetStationPrices?pageSize=5000",
        "type": "json",
    },
    "ok": {
        "url": "https://www.ok.dk/privat/paa-tanken/find-tank/gettankstationer",
        "type": "json",
    },
    "q8": {
        "url": "https://beta.q8.dk/Station/GetStationPrices?pageSize=5000",
        "type": "json",
    },
    "oil": {
        "url": "https://www.oil-tankstationer.dk/fileadmin/user_upload/dk/downloads-dk/OIL-DK_Priser-Privat_Gaeldende-priser_website_Excel.xlsx",
        "type": "xlsx",
    },
    "shell": {
        "url": "https://shellservice.dk/wp-content/uploads/sites/2/2026/01/dk-prices-14.01.2026.xlsx",
        "type": "xlsx",
    },
    "goon": {"url": "https://goon.nu", "type": "html"},
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def dump(name: str, url: str, ext_type: str) -> None:
    print(f"Fetching {name} from {url}")
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    # Define which extensions should be handled as binary
    BINARY_EXTENSIONS = {"xlsx", "xls", "zip", "png", "jpg"}

    out = FIXTURES_DIR / f"{name}.{ext_type}"

    if ext_type in BINARY_EXTENSIONS:
        # .content returns raw bytes, which is required for ZIP-based files like XLSX
        out.write_bytes(response.content)
    else:
        # .text returns a string, which is appropriate for JSON, HTML, etc.
        out.write_text(response.text, encoding="utf-8")

    print(f"Saved → {out}")


def main():
    for name, data in SITES.items():
        try:
            dump(name, data["url"], data["type"])
        except Exception as exc:
            print(f"❌ Failed to fetch {name}: {exc}")


if __name__ == "__main__":
    main()
