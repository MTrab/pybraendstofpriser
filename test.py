"""Test file for pybraendstofpriser module."""

import asyncio

from pybraendstofpriser import Braendstofpriser
from pybraendstofpriser.const import DIESEL, OCTANE_92, OCTANE_95


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser()
    product = OCTANE_92

    companies = await braendstofpriser.list_companies()
    # for company in companies:
    #     if not product in companies[company]["products"]:
    #         continue
    company = "Go’on"
    station = "Go’on Gjellerup"
    await braendstofpriser.set_company(company)
    stations = await braendstofpriser.list_stations(company)
    braendstofpriser.set_station(station)
    products = await braendstofpriser.list_products()
    price = await braendstofpriser.get_price(product)

    print("%s at %s costs %.2f kr/liter", product, station, price)


if __name__ == "__main__":
    asyncio.run(main())
