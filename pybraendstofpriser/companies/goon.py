"""Go'On fetcher for pybraendstofpriser."""

from __future__ import annotations

import logging

from ..const import DIESEL, OCTANE_92, OCTANE_95
from ..exceptions import ProductNotFoundError, StationNotFoundError
from ..tools import clean_product_name, clean_value, get_html_soup, get_website
from . import FuelCompanyBase, FuelStation

BASEURL = "https://goon.nu"

PRODUCTS = {
    OCTANE_92: {"name": "Blyfri 92"},
    OCTANE_95: {"name": "Blyfri 95"},
    DIESEL: {"name": "Diesel"},
}

COMPANY_NAME = "Go’on"

_LOGGER = logging.getLogger(__name__)


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(PRODUCTS)

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        r = await get_website(BASEURL, timeout=20)
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

                self._stations.append(
                    FuelStation(
                        id=None,  # type: ignore
                        name=station_name,
                        address=station_address,
                        prices={
                            OCTANE_92: fuel_92_price,
                            OCTANE_95: fuel_95_price,
                            DIESEL: diesel_price,
                        },
                    )
                )
