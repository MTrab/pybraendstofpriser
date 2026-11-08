![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)

## pybraendstofpriser

This is a PyPI module for fetching fuel prices from Fuelprices.dk API, primarily developed for use with [Home Assistant](https://home-assistant.io), but I try to keep it as widely usable as possible.

The API requires an API key to be used - see [https://fuelprices.dk](https://fuelprices.dk) for more information.

### Fetch prices for multiple stations

```python
from pybraendstofpriser import Braendstofpriser

client = Braendstofpriser("your-api-key")
stations = await client.get_prices_bulk([1234, 4321])

for item in stations:
    print(item["station"]["name"], item["prices"])
```

`get_prices_bulk` returns an `Flist` of station records with `company`, `station`,
`prices`, `price_units`, and `price_kinds`, preserving the API's values (including
prices as strings). It requests all current products for each station.

Up to 1,000 distinct station IDs are fetched in one HTTP request with a page size
of 1,000. Larger selections are split into groups of at most 1,000 IDs; any further
pages are fetched automatically. Duplicate IDs are requested once, and an empty
selection makes no requests. Result order follows the API within each group.

The API omits unknown, inactive, stale, and unpriced stations. HTTP errors are
raised to the caller, including errors on later groups or pages; partial results
are not returned. The existing `get_prices` method remains available for fetching
a single station.
