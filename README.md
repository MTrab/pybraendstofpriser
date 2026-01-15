![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)

## pybraendstofpriser

This is a PyPI module for fetching/scraping fuel prices from Danish suppliers, primarily developed for use with [Home Assistant](https://home-assistant.io), but I try to keep it as widely usable as possible.

### These companies are currently available:

*   [F24](https://www.f24.dk/)
*   [Go'On](https://goon.nu)
*   [OIL! tank & go](https://www.oil-tankstationer.dk)
*   [OK](https://www.ok.dk)
*   [Q8](https://www.q8.dk)
*   [Shell](https://shellservice.dk)

### These companies are currently not available in this module:

*   UnoX
*   ingo
*   CircleK

## Testing

This project uses pytest for testing. The suite is divided into two categories to ensure both reliability and real-world accuracy.

### Test Types

Unit Tests (Offline): These tests use local data dumps (fixtures) located in tests/fixtures/. They verify the parsing logic without requiring an internet connection.

Live Tests: These tests perform actual network requests to verify that fuel company websites are reachable and that their data structures haven't changed.

### Running the Tests

To run the standard test suite (recommended for CI and PRs):
```bash
poetry run pytest -v -m "not live"
```

To run the live integration tests (Do NOT run these from CI):
```bash
poetry run pytest -v
```