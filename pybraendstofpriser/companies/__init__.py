"""pybraendstofpriser companies package."""

from __future__ import annotations

from ..exceptions import ProductNotFoundError


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

    def fetch_price(self, product: str) -> float:
        """Fetch fuel prices."""
        for s in self._stations:
            if s.name == self.station:
                if s.prices.get(product) is None:
                    raise ProductNotFoundError(
                        f"Product '{self.products[product]['name']}'"
                        f" not found at station '{self.station}'"
                    )
                return s.prices.get(product)  # type: ignore
        raise ProductNotFoundError(
            f"Product '{self.products[product]['name']}' not found at station '{self.station}'"
        )

    async def list_products(self) -> list[str]:
        """List available fuel products."""
        retlist = []
        for _, product_dict in self.products.items():
            retlist.append(product_dict["name"])
        return retlist

    async def list_stations(self) -> list[dict]:
        """List available fuel stations."""
        if not self._stations:
            await self._load_stations()
        return self._stations  # type: ignore

    async def _load_stations(self) -> None:
        """Load fuel stations."""
        raise NotImplementedError


class FuelStation:
    """Fuel station class."""

    def __init__(self, sid: int, name: str, address: str, prices: dict) -> None:
        """Initialize the FuelStation class."""
        self._id = sid
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
