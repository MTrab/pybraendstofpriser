"""pybraendstofpriser companies package."""

from __future__ import annotations


class FuelCompanyBase:
    """Fuel company base class."""

    def __init__(self, products: dict) -> None:
        """Initialize the FuelCompany class."""
        self._stations: list[FuelStation] = []
        self.station: str | None = None
        self.products = products

    def get_product_name(self, product: str) -> str:
        """Get product name."""
        return self.products[product]["name"]

    async def fetch_price(self, product: str) -> float | None:
        """Fetch fuel prices."""
        raise NotImplementedError

    async def list_products(self) -> list[str]:
        """List available fuel products."""
        raise NotImplementedError

    async def list_stations(self) -> list[dict]:
        """List available fuel stations."""
        if not self._stations:
            await self._load_stations()
        return self._stations

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        raise NotImplementedError


class FuelStation:
    """Fuel station class."""

    def __init__(self, id: int, name: str, address: str, prices: dict) -> None:
        """Initialize the FuelStation class."""
        self._id = id
        self._name = name
        self._address = address
        self._prices = prices

    @property
    def id(self) -> int:
        """Get station ID."""
        return self._id

    @property
    def name(self) -> str:
        """Get station name."""
        return self._name

    @property
    def address(self) -> str:
        """Get station address."""
        return self._address

    @property
    def prices(self) -> dict:
        """Get station prices."""
        return self._prices
