"""Defines the pybraendstofpriser package."""

from __future__ import annotations

import importlib
import logging
import sys
from asyncio import get_running_loop
from collections import namedtuple
from os import listdir
from posixpath import dirname

from genericpath import isfile

from .companies import FuelCompanyBase
from .exceptions import StationNotFoundError

if sys.version_info < (3, 11, 0):
    sys.exit("The pybraendstofpriser module requires Python 3.11.0 or later")

_LOGGER = logging.getLogger(__name__)
Company = namedtuple("Company", "module namespace products name")


class Braendstofpriser:
    """Main class for pybraendstofpriser module."""

    def __init__(self):
        """Initialize the Braendstofpriser class."""
        self.companies = {}
        self.company: FuelCompanyBase

        _LOGGER.debug("Braendstofpriser initialized")

    async def list_companies(self):
        """List fuel companies."""
        _LOGGER.debug("Listing companies")
        loop = get_running_loop()
        companies = await loop.run_in_executor(
            None, listdir, f"{dirname(__file__)}/companies"
        )
        for company in sorted(companies):
            company_path = f"{dirname(__file__)}/companies/{company}"
            if (
                isfile(company_path)
                and not company.endswith("__pycache__")
                and not company == "__init__.py"
            ):
                company_name = company.replace(".py", "")
                _LOGGER.debug("Found company: %s", company_name)

                ns = f".companies.{company.replace('.py', '')}"
                mod = await self._load_module(ns)

                self.companies.update(
                    {
                        mod.COMPANY_NAME: {
                            "products": mod.PRODUCTS,
                            "namespace": ns,
                        }
                    }
                )

        return self.companies

    async def set_company(self, company: str):
        """Set the fuel company."""
        if len(self.companies) == 0:
            await self.list_companies()

        _LOGGER.debug("Setting company to %s", company)
        c = await self._load_module(self.companies[company]["namespace"])
        self.company = c.FuelCompany()

    def get_price(self, station: str, product: str):
        """Get fuel price for a specific company and product."""
        if self.company is None:
            raise ValueError("Company not set. Please set a company first.")

        _LOGGER.debug("Getting price for %s", product)
        return self.company.fetch_price(station, product)

    async def list_stations(self):
        """List fuel stations for a specific company."""
        if self.company is None:
            raise ValueError("Company not set. Please set a company first.")

        _LOGGER.debug("Listing stations for %s", self.company)
        return await self.company.list_stations()

    async def list_products(self, station):
        """List fuel products for a specific company and station."""
        _LOGGER.debug("Listing products for %s", station)
        return await self.company.list_products(station)

    @staticmethod
    async def _load_module(namespace: str):
        """Dynamically load a module."""
        loop = get_running_loop()
        return await loop.run_in_executor(
            None, importlib.import_module, namespace, __name__
        )
