"""OIL! tank & go fetcher for pybraendstofpriser."""

from __future__ import annotations

import logging

from ..const import BIO_DIESEL, DIESEL, OCTANE_95
from ..exceptions import ProductNotFoundError, StationNotFoundError
from ..tools import (
    clean_product_name,
    clean_value,
    get_xls_file,
)
from . import FuelCompanyBase, FuelStation

baseurl = "https://www.oil-tankstationer.dk/fileadmin/user_upload/dk/downloads-dk/OIL-DK_Priser-Privat_Gaeldende-priser_website_Excel.xlsx"

PRODUCTS = {
    DIESEL: {"name": "Diesel B7"},
    BIO_DIESEL: {"name": "BIO100 DIESEL"},
    OCTANE_95: {"name": "95 E10"},
}

COMPANY_NAME = "OIL! tank & go"

_LOGGER = logging.getLogger(__name__)


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(PRODUCTS)

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        station_list = await get_xls_file(baseurl)
        for row in station_list.itertuples():
            if not isinstance(row._2, str):
                continue

            if not row._2.startswith("OIL!"):  # Only iterate over valid stations
                continue

            station_id = row._1 if isinstance(row._1, int) else None
            station_name = clean_product_name(row._2)
            station_address = clean_product_name(row._3)
            fuel_95_price = clean_value(str(row._5))
            diesel_price = clean_value(str(row._6))
            bio_diesel_price = clean_value(str(row._7))
            self._stations.append(
                FuelStation(
                    id=station_id,  # type: ignore
                    name=station_name,
                    address=station_address,
                    prices={
                        OCTANE_95: fuel_95_price,
                        DIESEL: diesel_price,
                        BIO_DIESEL: bio_diesel_price,
                    },
                )
            )

    async def list_products(self) -> list[str]:
        """List available fuel products."""
        if not self._stations:
            await self._load_stations()

        for s in self._stations:
            if s.name == self.station:
                retlist = []
                for product, price in s.prices.items():
                    if price is not None:
                        retlist.append(PRODUCTS[product]["name"])
                return retlist

        raise StationNotFoundError(
            f"Station '{self.station}' not found. Cannot list products."
        )

    async def fetch_price(self, product: str) -> float:
        """Fetch fuel prices."""
        for s in self._stations:
            if s.name == self.station:
                if s.prices.get(product) is None:
                    raise ProductNotFoundError(
                        f"Product '{self.get_product_name(product)}' not found at station '{self.station}'"
                    )
                return s.prices.get(product)

        raise ProductNotFoundError(
            f"Product '{self.get_product_name(product)}' not found at station '{self.station}'"
        )
