"""pybraendstofpriser companies package."""

from __future__ import annotations

from ..exceptions import ProductNotFoundError


class FuelCompanyBase:
    """Fuel company base class."""

    def __init__(self, products: dict) -> None:
        """Initialize the FuelCompany class."""
        self._stations: list[FuelStation] = []
        self.products = products
        self._station_obj: FuelStation

    def get_product_name(self, product: str) -> str:
        """Get product name."""
        return self.products[product]["name"]

    def fetch_price(self, station: str, product: str) -> float:
        """Fetch fuel prices."""
        for s in self._stations:
            if s.name == station:
                if s.prices.get(product) is None:
                    raise ProductNotFoundError(
                        f"Product '{self.products[product]['name']}'"
                        f" not found at stations '{station}'"
                    )
                return s.prices.get(product)  # type: ignore
        raise ProductNotFoundError(
            f"Product '{self.products[product]['name']}' not found at station '{station}'"
        )

    async def list_products(self, station) -> list[str]:
        """List available fuel products."""
        retlist = []
        for s in self._stations:
            if s.name == station:
                for product, price in s.prices.items():
                    if not isinstance(price, type(None)):
                        retlist.append(product)
                break

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

    def __init__(
        self,
        sid: int,
        name: str,
        address: str,
        prices: dict,
        lat: float = 0.00,
        lon: float = 0.00,
    ) -> None:
        """Initialize the FuelStation class."""
        self._id = sid
        self._name = name
        self._address = address
        self._prices = prices
        self._lat = lat
        self._lon = lon

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

    @property
    def latitude(self) -> float:
        """Get station latitude."""
        return self._lat

    @property
    def longitude(self) -> float:
        """Get station longitude."""
        return self._lon
