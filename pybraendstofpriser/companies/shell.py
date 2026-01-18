"""Shell fetcher for pybraendstofpriser."""

from __future__ import annotations

from ..const import DIESEL, DIESEL_PLUS, OCTANE_95, OCTANE_100
from ..tools import clean_product_name, clean_value, get_xls_file
from . import FuelCompanyBase, FuelStation

BASEURL = "https://shellservice.dk/wp-content/uploads/sites/2/2026/01/dk-prices-14.01.2026.xlsx"
# TODO: Find locations for stations

PRODUCTS = {
    DIESEL: {"name": "Shell FuelSave Diesel"},
    DIESEL_PLUS: {"name": "Shell V-Power Diesel"},
    OCTANE_95: {"name": "Shell FuelSave 95 oktan"},
    OCTANE_100: {"name": "Shell V-Power 100 oktan"},
}

COMPANY_NAME = "Shell"


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(COMPANY_NAME, PRODUCTS)

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        station_list = await get_xls_file(BASEURL)
        for row in station_list.itertuples():
            # Ensure row[2] (Address) and row[1] (Name) are valid strings
            if not isinstance(row[2], str) or not isinstance(row[1], str):
                continue

            if not row[1].startswith("Shell"):  # Only iterate over valid stations
                continue

            station_id = row[0] if isinstance(row[0], int) else None
            station_name = clean_product_name(row[1])
            station_address = clean_product_name(
                str(row[2]) + " " + str(row[3]) + " " + str(row[4])
            )
            fs95_price = clean_value(str(row[5]))
            vp100_price = clean_value(str(row[6]))
            fsd_price = clean_value(str(row[7]))
            vpd_price = clean_value(str(row[8]))
            self._stations.append(
                FuelStation(
                    sid=station_id,  # type: ignore
                    name=station_name,
                    address=station_address,
                    prices={
                        OCTANE_95: fs95_price,
                        OCTANE_100: vp100_price,
                        DIESEL: fsd_price,
                        DIESEL_PLUS: vpd_price,
                    },
                )
            )
