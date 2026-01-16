"""Test file for pybraendstofpriser module."""

import asyncio
import random

from pybraendstofpriser import Braendstofpriser


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser()

    companies = await braendstofpriser.list_companies()
    company = random.choice(list(companies.keys()))
    await braendstofpriser.set_company(company)
    stations = await braendstofpriser.list_stations()
    station = (random.choice(stations)).name
    products = await braendstofpriser.list_products(station)
    product = random.choice(products)

    price = braendstofpriser.get_price(station, product)

    print(
        f"{company} product {braendstofpriser.company.get_product_name(product)} at {station} costs {price:.2f} kr/liter"
    )


if __name__ == "__main__":
    asyncio.run(main())
