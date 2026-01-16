"""Test file for pybraendstofpriser module."""

import asyncio
import random

from pybraendstofpriser import Braendstofpriser


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser()

    def sorter(e):
        return e.name

    # companies = await braendstofpriser.list_companies()
    # company = random.choice(list(companies.keys()))
    company = "OK"
    await braendstofpriser.set_company(company)
    stations = await braendstofpriser.list_stations()
    stations.sort(key=sorter)

    # station = (random.choice(stations)).name
    station = "Voldby, Dolmervej"
    products = await braendstofpriser.list_products(station)
    product = random.choice(products)

    price = braendstofpriser.get_price(station, product)

    print(
        f"{company} product {braendstofpriser.company.get_product_name(product)} at {station} costs {price:.2f} kr/liter"
    )


if __name__ == "__main__":
    asyncio.run(main())
