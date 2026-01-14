"""OK fetcher for pybraendstofpriser."""

from __future__ import annotations
import logging

from . import FuelCompanyBase, FuelStation

from ..exceptions import ProductNotFoundError
from ..const import DIESEL, OCTANE_100, OCTANE_95
from ..tools import clean_product_name, clean_value, get_html_soup, get_website

baseurl = "https://www.ok.dk/privat/paa-tanken/find-tank/gettankstationer"

PRODUCTS = {
    DIESEL: {"name": "Svovlfri Diesel"},
    OCTANE_95: {"name": "Blyfri 95"},
    OCTANE_100: {"name": "Oktan 100"},
}

COMPANY_NAME = "OK"

_LOGGER = logging.getLogger(__name__)


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(PRODUCTS)

    async def fetch_price(self, product: str) -> float:
        """Fetch fuel prices."""
        for s in self._stations:
            if s["name"] == self.station:
                if s["prices"].get(product) is None:
                    raise ProductNotFoundError(
                        f"Product '{PRODUCTS[product]['name']}' not found at station '{self.station}'"
                    )
                return s["prices"].get(product)

        raise ProductNotFoundError(
            f"Product '{PRODUCTS[product]['name']}' not found at station '{self.station}'"
        )

    async def list_products(self) -> list[str]:
        """List available fuel products."""
        retlist = []
        for _, productDict in PRODUCTS.items():
            retlist.append(productDict["name"])
        return retlist

    def get_product_name(self, product: str) -> str:
        """Get product name."""
        return PRODUCTS[product]["name"]

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        self._stations.clear()
        r = await get_website(baseurl, timeout=5, as_json=True)
        stations = r["tankstationer"]

        for station in stations:
            if (
                isinstance(station["produkter"], type(None))
                or len(station["produkter"]) == 0
            ):
                # No products at this station
                continue

            station_id = station["id"] if isinstance(station["id"], int) else None
            station_name = clean_product_name(station["navn"])
            station_address = clean_product_name(station["adresse"])

            fuel_95_price = None
            fuel_100_price = None
            diesel_price = None

            for product in station["produkter"]:
                if product["navn"] == PRODUCTS[OCTANE_95]["name"]:
                    fuel_95_price = clean_value(product["pris"])
                elif product["navn"] == PRODUCTS[OCTANE_100]["name"]:
                    fuel_100_price = clean_value(product["pris"])
                elif product["navn"] == PRODUCTS[DIESEL]["name"]:
                    diesel_price = clean_value(product["pris"])

            self._stations.append(
                FuelStation(
                    id=station_id,  # type: ignore
                    name=station_name,
                    address=station_address,
                    prices={
                        OCTANE_95: fuel_95_price,
                        OCTANE_100: fuel_100_price,
                        DIESEL: diesel_price,
                    },
                )
            )
