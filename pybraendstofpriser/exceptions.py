"""Exceptions for pybraendstofpriser."""


class ErrorFetchingData(Exception):
    """Exception raised for errors in fetching data from the website."""


class ProductNotFoundError(Exception):
    """Exception raised for errors in fetching a specific product."""


class StationNotFoundError(Exception):
    """Exception raised when a station is not found."""
