"""Tests for pybraendstofpriser, including fixture-based unit tests and live integration tests."""

import pytest
import random


@pytest.mark.asyncio
async def test_smoke_init(api):
    """Smoke test: Can we initialize the class?"""
    assert api is not None


@pytest.mark.asyncio
async def test_smoke_list_companies(api):
    """Smoke test: Can we see the list of supported companies?"""
    companies = await api.list_companies()
    assert "F24" in companies
    assert "Go’on" in companies
    assert "OIL! tank & go" in companies
    assert "OK" in companies
    assert "Q8" in companies
    assert "Shell" in companies


COMPANIES_DATA = [
    # (Name, Fixture-file, Fetcher-function, Default product for live test)
    ("F24", "f24", "f24.json", "get_website"),
    ("Go’on", "goon", "goon.html", "get_website"),
    ("OIL! tank & go", "oil", "oil.xlsx", "get_xls_file"),
    ("OK", "ok", "ok.json", "get_website"),
    ("Q8", "q8", "q8.json", "get_website"),
    ("Shell", "shell", "shell.xlsx", "get_xls_file"),
]


@pytest.mark.parametrize(
    "company_name, module_name,fixture_name, fetcher",
    COMPANIES_DATA,
    ids=[item[0] for item in COMPANIES_DATA],  # Use company name as test ID
)
@pytest.mark.asyncio
async def test_company_parsing_from_fixtures(
    api, load_fixture, mocker, company_name, module_name, fixture_name, fetcher
):
    """Test parsing for each company by mocking the network fetcher in the tools module."""
    mock_data = load_fixture(fixture_name)

    mocker.patch(
        f"pybraendstofpriser.companies.{module_name}.{fetcher}",
        new_callable=mocker.AsyncMock,
        return_value=mock_data,
    )

    await api.set_company(company_name)
    stations = await api.list_stations()

    assert (
        len(stations) > 0
    ), f"Could not find stations for {company_name} in {fixture_name}"
    assert stations[0].name is not None


@pytest.mark.live
@pytest.mark.parametrize(
    "company_name, _, __, ___",
    COMPANIES_DATA,
    ids=[item[0] for item in COMPANIES_DATA],  # Use company name as test ID
)
@pytest.mark.asyncio
async def test_live_fetch_all_companies(api, company_name, _, __, ___):
    """Dynamic live test: Checks that we can fetch prices from all companies live."""
    await api.set_company(company_name)
    stations = await api.list_stations()
    assert len(stations) > 0, f"No live stations found for {company_name}"

    selected_station = random.choice(stations)
    await api.set_station(selected_station.name)

    products = await api.list_products()
    product = random.choice(products)
    price = api.get_price(product)

    assert isinstance(price, float), f"Price for {company_name} is not a float"
    assert price > 0, f"Price for {company_name} must be greater than 0"
