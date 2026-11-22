"""Connector module for communicating with fuel price services."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any, Optional

import aiohttp

from .const import API_ENDPOINT, API_TIMEOUT


def _default_user_agent() -> str:
    """Resolve the installed package version using distribution metadata."""
    try:
        package_version = version("pybraendstofpriser")
    except PackageNotFoundError:
        package_version = "unknown"
    return f"pybraendstofpriser/{package_version}"


_DEFAULT_USER_AGENT = _default_user_agent()


class Endpoint:
    """Class containing API endpoint definitions."""

    PRICES = "/prices"
    STATIONS = "/stations"
    STATIONS_BULK = "/stations/bulk"
    COMPANIES = "/companies"


class Connector:
    """Connector class for handling HTTP communication."""

    def __init__(self, apikey: str, *, user_agent: str | None = None):
        """Initialize the Connector class."""
        self.apikey = apikey
        self._user_agent = _DEFAULT_USER_AGENT if user_agent is None else user_agent

    async def fetch_data(self, endpoint: str, args: Optional[dict] = None) -> Any:
        """Fetch data from the specified endpoint.

        Args:
            endpoint (Endpoint): The API endpoint to fetch data from.
            args (dict): Query parameters for the request.
        Returns:
            dict: The JSON response from the API.
        """
        url = f"{API_ENDPOINT}{endpoint}"
        headers = {"X-API-KEY": self.apikey, "User-Agent": self._user_agent}
        timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=args, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
