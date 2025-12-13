"""Tools package for pybraendstofpriser."""

from __future__ import annotations
import logging
import aiohttp
from bs4 import BeautifulSoup as BS

_LOGGER = logging.getLogger(__name__)


@staticmethod
async def get_website(url: str, timeout: int = 10):
    """Fetch content from a website asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                return await response.text()
    except aiohttp.ClientError as e:
        _LOGGER.error("Error fetching %s: %s", url, e)
        return None


@staticmethod
def get_html_soup(r, parser="html.parser"):
    """Parse HTML content using BeautifulSoup."""
    return BS(r, parser)


@staticmethod
def clean_product_name(productName):
    """Clean and standardize product name."""
    productName = productName.replace("Beskrivelse: ", "")
    productName = productName.strip()
    return productName


@staticmethod
def clean_value(value) -> float | None:
    """Clean and convert value to float."""
    value = value.replace("kr.", "").replace(",", ".").strip()
    try:
        return float(value)
    except ValueError:
        _LOGGER.error("Error converting value to float: %s", value)
        return None
