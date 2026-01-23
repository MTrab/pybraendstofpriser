"""Test file for pybraendstofpriser module."""

import asyncio
from datetime import datetime
import random
from os import environ

from aiohttp import ClientResponseError

from pybraendstofpriser import Braendstofpriser


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser(environ["APIKEY"])
    try:
        companies = await braendstofpriser.list_companies()
        company = companies[random.choice(list(companies.keys()))]
        stations = await braendstofpriser.list_stations(company_name=company["name"])
        stations = {
            k: v
            for k, v in sorted(stations.items(), key=lambda item: item[1]["name"])
        }
        station_key = random.choice(list(stations.keys()))
        prices = await braendstofpriser.get_prices(station_id=station_key)
        product = random.choice(list(prices["prices"].keys()))
        price = prices["prices"][product]

        last_update = (
            "at "
            + datetime.fromisoformat(prices["updated_at"]).strftime("%d-%m-%Y %H:%M:%S")
            if not isinstance(prices["updated_at"], type(None))
            else "unknown"
        )

        print(
            f"{company["name"]} product {product} at {stations[station_key]["name"]} costs {price:.2f} kr/liter and last update was {last_update}."
        )
    except ClientResponseError as exc:  # pylint: disable=broad-except
        if exc.status == 401:
            print("invalid_api_key")


if __name__ == "__main__":
    asyncio.run(main())
