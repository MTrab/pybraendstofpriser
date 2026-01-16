"""OIL! tank & go fetcher for pybraendstofpriser."""

from __future__ import annotations

from ..const import BIO_DIESEL, DIESEL, OCTANE_95
from ..tools import clean_product_name, clean_value, get_xls_file
from . import FuelCompanyBase, FuelStation

BASEURL = "https://www.oil-tankstationer.dk/fileadmin/user_upload/dk/downloads-dk/OIL-DK_Priser-Privat_Gaeldende-priser_website_Excel.xlsx"  # pylint: disable=C0301

PRODUCTS = {
    DIESEL: {"name": "Diesel B7"},
    BIO_DIESEL: {"name": "BIO100 DIESEL"},
    OCTANE_95: {"name": "95 E10"},
}

COMPANY_NAME = "OIL! tank & go"


class FuelCompany(FuelCompanyBase):
    """Fuel company class."""

    def __init__(self) -> None:
        """Initialize the FuelCompany class."""
        super().__init__(COMPANY_NAME, PRODUCTS)

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        station_list = await get_xls_file(BASEURL)
        for row in station_list.itertuples():
            if not isinstance(row[2], str):
                continue

            if not row[2].startswith("OIL!"):  # Only iterate over valid stations
                continue
            loc_tmp = row[4].replace(" N", "").replace(" E", "")
            location = loc_tmp.split(",")
            if len(location) == 1:
                # Sometimes they forget the comma seperator
                location = loc_tmp.split(" ")

            station_id = row[1] if isinstance(row[1], int) else None
            station_name = clean_product_name(row[2])
            station_address = clean_product_name(row[3])
            latitude = location[0].strip()
            longitude = location[1].strip()
            fuel_95_price = clean_value(str(row[5]))
            diesel_price = clean_value(str(row[6]))
            bio_diesel_price = clean_value(str(row[7]))
            self._stations.append(
                FuelStation(
                    sid=station_id,  # type: ignore
                    name=station_name,
                    address=station_address,
                    prices={
                        OCTANE_95: fuel_95_price,
                        DIESEL: diesel_price,
                        BIO_DIESEL: bio_diesel_price,
                    },
                    lat=latitude,
                    lon=longitude,
                )
            )
