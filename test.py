"""Test file for pybraendstofpriser module."""

import asyncio

from pybraendstofpriser import Braendstofpriser
from pybraendstofpriser.const import DIESEL, OCTANE_92, OCTANE_95


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser()
    product = OCTANE_95

    companies = await braendstofpriser.list_companies()
    company = "OIL! tank & go"
    station = "OIL! tank & go Bolbro, Odense"
    await braendstofpriser.set_company(company)
    stations = await braendstofpriser.list_stations(company)
    braendstofpriser.set_station(station)
    products = await braendstofpriser.list_products()
    price = await braendstofpriser.get_price(product)

    print(
        f"{braendstofpriser.company.get_product_name(product)} at {station} costs {price:.2f} kr/liter"
    )


if __name__ == "__main__":
    asyncio.run(main())
