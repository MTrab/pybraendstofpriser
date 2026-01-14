"""F24 fetcher for pybraendstofpriser."""

from __future__ import annotations

from ..const import BIO_DIESEL, DIESEL, DIESEL_PLUS, OCTANE_92, OCTANE_95
from ..tools import clean_product_name, clean_value, get_website
from . import FuelCompanyBase, FuelStation

BASEURL = "https://beta.q8.dk/Station/GetStationPrices?pageSize=5000"

PRODUCTS = {
    DIESEL: {"name": "GoEasy Diesel"},
    DIESEL_PLUS: {"name": "GoEasy Diesel Extra"},
    BIO_DIESEL: {"name": "Neste MY (HVO100)"},
    OCTANE_95: {"name": "GoEasy 95 E10"},
    OCTANE_92: {"name": "GoEasy 95 Extra E5"},
}

COMPANY_NAME = "F24"


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(PRODUCTS)

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        self._stations.clear()
        r = await get_website(BASEURL, timeout=10, as_json=True)
        stations = r["data"]["stationsPrices"]  # type: ignore

        station_id = None
        station_name = None
        station_address = None
        products = {}

        for station in stations:  # type: ignore

            if not isinstance(station_id, type(None)):
                if station_id != station["stationId"]:  # type: ignore
                    self._stations.append(
                        FuelStation(
                            station_id,  # type: ignore
                            station_name,  # type: ignore
                            station_address,  # type: ignore
                            products,
                        )
                    )

            if isinstance(station["address"], type(None)):  # type: ignore
                continue

            if not station["stationName"].startswith("F24"):  # type: ignore
                # Not a F24 station, skip this record
                continue

            station_id = station["stationId"]  # type: ignore
            arraddress = station["address"].split(" ")  # type: ignore
            station_name = station["stationName"] + ", " + arraddress[0]  # type: ignore
            prod = clean_product_name(station["products"][0]["productName"])  # type: ignore
            product = None
            for key, value in PRODUCTS.items():
                if value["name"] == prod:
                    product = key
                    break

            if not isinstance(product, type(None)):
                price = clean_value(station["products"][0]["price"])  # type: ignore
                products.update({product: price})
