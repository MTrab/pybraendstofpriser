"""Test file for pybraendstofpriser module."""

import asyncio

from pybraendstofpriser import Braendstofpriser
from pybraendstofpriser.const import DIESEL, OCTANE_95


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser()
    product = OCTANE_95

    companies = await braendstofpriser.list_companies()
    for company in companies:
        if not product in companies[company]["products"]:
            continue

        price = await braendstofpriser.get_price(company, product)
        print(
            f"Price for {company} - {companies[company]['products'][OCTANE_95]['name']}:",
            price,
        )


if __name__ == "__main__":
    asyncio.run(main())
