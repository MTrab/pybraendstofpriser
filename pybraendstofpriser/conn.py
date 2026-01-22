"""Connector module for communicating with fuel price services."""

from __future__ import annotations
import aiohttp

from .const import API_ENDPOINT, API_TIMEOUT


class Endpoint:
    """Class containing API endpoint definitions."""

    PRICES = "/prices"
    STATIONS = "/stations"
    COMPANIES = "/companies"


class Connector:
    """Connector class for handling HTTP communication."""

    def __init__(self, apikey: str):
        """Initialize the Connector class."""
        self.session = aiohttp.ClientSession()
        self.apikey = apikey

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def fetch_data(self, endpoint: str, args: Optional[Dict] = None) -> dict:
        """Fetch data from the specified endpoint.

        Args:
            endpoint (Endpoint): The API endpoint to fetch data from.
            args (dict): Query parameters for the request.
        Returns:
            dict: The JSON response from the API.
        """
        url = f"{API_ENDPOINT}{endpoint}"
        headers = {"X-API-KEY": self.apikey}
        timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)

        async with self.session.get(
            url, params=args, headers=headers, timeout=timeout
        ) as response:
            response.raise_for_status()
            return await response.json()
