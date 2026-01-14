"""Defines the pybraendstofpriser package."""

from __future__ import annotations
from asyncio import get_running_loop
from collections import namedtuple
from genericpath import isfile
import importlib
import logging
from os import listdir
from posixpath import dirname
import sys

from .companies import FuelCompanyBase

if sys.version_info < (3, 11, 0):
    sys.exit("The pybraendstofpriser module requires Python 3.11.0 or later")

_LOGGER = logging.getLogger(__name__)
Company = namedtuple("Company", "module namespace products name")


class Braendstofpriser:
    """Main class for pybraendstofpriser module."""

    def __init__(self):
        """Initialize the Braendstofpriser class."""
        # self.companies = []
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
        _LOGGER.debug("Setting company to %s", company)
        c = await self._load_module(self.companies[company]["namespace"])
        self.company = c.FuelCompany()

    def set_station(self, station: str):
        """Set the fuel station for the current company."""
        if self.company is None:
            raise ValueError("Company not set. Please set a company first.")

        _LOGGER.debug("Setting station to %s", station)
        self.company.station = station

    async def get_price(self, product: str):
        """Get fuel price for a specific company and product."""
        if self.company is None:
            raise ValueError("Company not set. Please set a company first.")

        _LOGGER.debug("Getting price for %s", product)
        return await self.company.fetch_price(product)

    async def list_stations(self, company: str):
        """List fuel stations for a specific company."""
        if self.company is None:
            raise ValueError("Company not set. Please set a company first.")

        _LOGGER.debug("Listing stations for %s", company)
        return await self.company.list_stations()

    async def list_products(self):
        """List fuel products for a specific company and station."""
        if self.company.station is None:
            raise ValueError("Station not set. Please set a station first.")

        _LOGGER.debug("Listing products for %s", self.company.station)
        return await self.company.list_products()

    @staticmethod
    async def _load_module(namespace: str):
        """Dynamically load a module."""
        loop = get_running_loop()
        return await loop.run_in_executor(
            None, importlib.import_module, namespace, __name__
        )
