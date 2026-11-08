"""Defines the pybraendstofpriser package."""

from __future__ import annotations

import logging
import sys
from collections import namedtuple
from collections.abc import Sequence

from .conn import Connector, Endpoint
from .exceptions import StationNotFoundError

if sys.version_info < (3, 11, 0):
    sys.exit("The pybraendstofpriser module requires Python 3.11.0 or later")

_LOGGER = logging.getLogger(__name__)
Company = namedtuple("Company", "module namespace products name")
_BULK_STATION_LIMIT = 1000


class Flist(list):
    def find(self, key, value) -> dict | None:
        for o in self:
            if o.get(key) == value:
                return o

        return None


class Braendstofpriser:
    """Main class for pybraendstofpriser module."""

    def __init__(self, apikey: str):
        """Initialize the Braendstofpriser class."""
        self.conn = Connector(apikey)
        _LOGGER.debug("Braendstofpriser initialized")

    async def list_companies(self) -> Flist[dict]:
        """List available fuel companies.

        Returns:
            dict: A dictionary of available fuel companies.
        """
        return Flist(await self.conn.fetch_data(Endpoint.COMPANIES))

    async def list_stations(
        self, company_id: int | None = None, company_name: str | None = None
    ) -> Flist[dict]:
        """List fuel stations for a given company.

        Args:
            company_id (int): The company ID.
            company_name (str): The company name (Case-sensitive).
        """
        args = {}
        if company_id is not None:
            args["company_id"] = company_id
        elif company_name is not None:
            args["company_name"] = company_name

        return Flist(await self.conn.fetch_data(Endpoint.STATIONS, args))

    async def get_prices(
        self,
        station_id: int,
    ) -> dict:
        """Get fuel prices for a given station.

        Args:
            station_id (int): The station ID.

        Returns:
            dict: A dictionary of company information, station information, and fuel prices.
        """
        args = {"station_id": station_id}

        return await self.conn.fetch_data(Endpoint.PRICES, args)

    async def get_prices_bulk(self, station_ids: Sequence[int]) -> Flist[dict]:
        """Get all current products for the requested stations.

        Split IDs into groups of at most 1000 and fetch all pages per group.
        Return the API records unchanged; raise on any failed request.
        """
        unique_ids = list(dict.fromkeys(station_ids))
        stations = Flist()
        for start in range(0, len(unique_ids), _BULK_STATION_LIMIT):
            batch = unique_ids[start : start + _BULK_STATION_LIMIT]
            page = 1
            while True:
                data = await self.conn.fetch_data(
                    Endpoint.STATIONS_BULK,
                    {
                        "station_ids": ",".join(
                            str(station_id) for station_id in batch
                        ),
                        "page": page,
                        "page_size": _BULK_STATION_LIMIT,
                    },
                )
                stations.extend(data["items"])
                if page >= data["total_pages"]:
                    break
                page += 1

        return stations
