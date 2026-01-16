"""OK fetcher for pybraendstofpriser."""

from __future__ import annotations

from ..const import DIESEL, OCTANE_95, OCTANE_100
from ..tools import clean_product_name, clean_value, get_website
from . import FuelCompanyBase, FuelStation

BASEURL = "https://www.ok.dk/privat/paa-tanken/find-tank/gettankstationer"

PRODUCTS = {
    DIESEL: {"name": "Svovlfri Diesel"},
    OCTANE_95: {"name": "Blyfri 95"},
    OCTANE_100: {"name": "Oktan 100"},
}

COMPANY_NAME = "OK"


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(COMPANY_NAME, PRODUCTS)

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        self._stations.clear()
        r = await get_website(BASEURL, timeout=5, as_json=True)
        stations = r["tankstationer"]  # type: ignore

        for station in stations:
            if (
                isinstance(station["produkter"], type(None))  # type: ignore
                or len(station["produkter"]) == 0  # type: ignore
            ):
                # No products at this station
                continue

            station_id = station["id"] if isinstance(station["id"], int) else None  # type: ignore
            station_name = clean_product_name(station["navn"])  # type: ignore
            station_address = clean_product_name(station["adresse"])  # type: ignore

            fuel_95_price = None
            fuel_100_price = None
            diesel_price = None

            for product in station["produkter"]:  # type: ignore
                if product["navn"] == PRODUCTS[OCTANE_95]["name"]:  # type: ignore
                    fuel_95_price = clean_value(product["pris"])  # type: ignore
                elif product["navn"] == PRODUCTS[OCTANE_100]["name"]:  # type: ignore
                    fuel_100_price = clean_value(product["pris"])  # type: ignore
                elif product["navn"] == PRODUCTS[DIESEL]["name"]:  # type: ignore
                    diesel_price = clean_value(product["pris"])  # type: ignore

            self._stations.append(
                FuelStation(
                    sid=station_id,  # type: ignore
                    name=station_name,
                    address=station_address,
                    prices={
                        OCTANE_95: fuel_95_price,
                        OCTANE_100: fuel_100_price,
                        DIESEL: diesel_price,
                    },
                    lat=float(station["latitude"]),  # type: ignore
                    lon=float(station["longtitude"]),  # type: ignore
                )
            )
