"""Go'On fetcher for pybraendstofpriser."""

from __future__ import annotations
import logging

from ..exceptions import ProductNotFoundError, StationNotFoundError
from ..const import DIESEL, OCTANE_92, OCTANE_95
from ..tools import (
    clean_value,
    clean_product_name,
    get_html_soup,
    get_website,
)

host = "https://goon.nu"
baseurl = f"{host}"

PRODUCTS = {
    OCTANE_92: {"name": "Blyfri 92"},
    OCTANE_95: {"name": "Blyfri 95"},
    DIESEL: {"name": "Diesel"},
}

COMPANY_NAME = "Go’on"

_LOGGER = logging.getLogger(__name__)


class FuelCompany:
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        self.__stations: list[dict] = []
        self.station: str | None = None

    async def fetch_price(self, product: str) -> float:
        """Fetch fuel prices."""
        for s in self.__stations:
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
        if not self.__stations:
            await self._load_stations()

        for s in self.__stations:
            if s["name"] == self.station:
                retlist = []
                for product, price in s["prices"].items():
                    if price is not None:
                        retlist.append(PRODUCTS[product]["name"])
                return retlist

        raise StationNotFoundError(
            f"Station '{self.station}' not found. Cannot list products."
        )

    async def list_stations(self) -> list[dict]:
        """List available fuel stations."""
        if not self.__stations:
            await self._load_stations()
        return self.__stations

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        r = await get_website(baseurl, timeout=5)
        html = get_html_soup(r)
        station_set = html.find_all("div", {"class": "table-scroll-wrapper"})
        stations = station_set[0].find_all("tr")

        for row in stations:
            cells = row.find_all("td")
            if cells:
                name_address = [
                    get_html_soup(_).text.strip() for _ in str(cells[0]).split("<br/>")
                ]
                station_name = clean_product_name(name_address[0])
                station_address = (
                    clean_product_name(name_address[1]) if len(name_address) > 1 else ""
                )
                fuel_92_price = clean_value(cells[1].text)
                fuel_95_price = clean_value(cells[2].text)
                diesel_price = clean_value(cells[3].text)
                self.__stations.append(
                    {
                        "name": station_name,
                        "address": station_address,
                        "prices": {
                            OCTANE_92: fuel_92_price,
                            OCTANE_95: fuel_95_price,
                            DIESEL: diesel_price,
                        },
                    }
                )
