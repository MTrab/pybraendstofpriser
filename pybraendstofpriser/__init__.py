"""Defines the pybraendstofpriser package."""

from __future__ import annotations

import logging
import sys
from collections import namedtuple

from .exceptions import StationNotFoundError

from .conn import Connector, Endpoint

if sys.version_info < (3, 11, 0):
    sys.exit("The pybraendstofpriser module requires Python 3.11.0 or later")

_LOGGER = logging.getLogger(__name__)
Company = namedtuple("Company", "module namespace products name")


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
