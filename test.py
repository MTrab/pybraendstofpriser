"""Test file for pybraendstofpriser module."""

import asyncio
from datetime import datetime
import random
from os import environ

from aiohttp import ClientResponseError

from pybraendstofpriser import Braendstofpriser, Flist


async def main():
    """Main test function."""
    braendstofpriser = Braendstofpriser(environ["APIKEY"])
    try:
        companies = await braendstofpriser.list_companies()
        company = random.choice(companies)
        # stations = await braendstofpriser.list_stations(company_name=company["company"])
        stations = await braendstofpriser.list_stations(company_name="Uno-X")
        sid = 2607
        # station = braendstofpriser.find(stations, "id", sid)
        station = stations.find("id", sid)
        station = random.choice(stations)
        prices = await braendstofpriser.get_prices(station_id=station["id"])
        product = random.choice(list(prices["prices"].keys()))
        price = prices["prices"][product]

        c_name = prices["company"]["company"]
        s_name = prices["station"]["name"]
        last_update = (
            "at "
            + datetime.fromisoformat(prices["station"]["last_update"]).strftime(
                "%d-%m-%Y %H:%M:%S"
            )
            if not isinstance(prices["station"]["last_update"], type(None))
            else "unknown"
        )

        print(
            f"{c_name} product {product} at {s_name} costs {price:.2f} kr/liter and last update was {last_update}."
        )
    except ClientResponseError as exc:  # pylint: disable=broad-except
        if exc.status == 401:
            print("invalid_api_key")


if __name__ == "__main__":
    asyncio.run(main())
