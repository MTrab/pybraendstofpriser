"""Tests for bulk station prices."""

import unittest
from unittest.mock import AsyncMock, Mock, call, patch

from aiohttp import ClientResponseError, web
from aiohttp.test_utils import TestServer

from pybraendstofpriser import Braendstofpriser, Flist
from pybraendstofpriser.conn import Endpoint


def station(station_id: int) -> dict:
    """Build a station record matching the bulk response schema."""
    return {
        "company": {"id": 1, "company": "Circle K"},
        "station": {"id": station_id, "name": f"Station {station_id}"},
        "prices": {"Blyfri95": "14.29", "Diesel": "12.99"},
        "price_units": {"Blyfri95": "DKK/L", "Diesel": "DKK/L"},
        "price_kinds": {"Blyfri95": "fuel", "Diesel": "fuel"},
    }


def response(items: list[dict], page: int = 1, total_pages: int = 1) -> dict:
    """Build a bulk response page."""
    return {
        "items": items,
        "page": page,
        "page_size": 1000,
        "total": len(items),
        "total_pages": total_pages,
    }


class BulkPricesTest(unittest.IsolatedAsyncioTestCase):
    """Test batching, pagination, and failure handling."""

    def setUp(self) -> None:
        self.client = Braendstofpriser("test-key")
        self.fetch = AsyncMock(return_value=response([]))
        self.patch = patch.object(self.client.conn, "fetch_data", self.fetch)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    async def test_prices_and_metadata(self) -> None:
        items = [station(1234), station(4321)]
        self.fetch.return_value = response(items)

        result = await self.client.get_prices_bulk([1234, 4321])

        self.assertIsInstance(result, Flist)
        self.assertEqual(result, items)
        self.fetch.assert_awaited_once_with(
            Endpoint.STATIONS_BULK,
            {"station_ids": "1234,4321", "page": 1, "page_size": 1000},
        )

    async def test_empty_selection(self) -> None:
        self.assertEqual(await self.client.get_prices_bulk([]), [])
        self.fetch.assert_not_awaited()

    async def test_duplicate_ids(self) -> None:
        await self.client.get_prices_bulk([1234, 1234, 4321])

        self.fetch.assert_awaited_once_with(
            Endpoint.STATIONS_BULK,
            {"station_ids": "1234,4321", "page": 1, "page_size": 1000},
        )

    async def test_batch_sizes(self) -> None:
        for count in (1, 999, 1000, 1001, 2000, 2001):
            with self.subTest(count=count):
                self.fetch.reset_mock()
                ids = list(range(1, count + 1))
                await self.client.get_prices_bulk(ids)

                expected_calls = [
                    call(
                        Endpoint.STATIONS_BULK,
                        {
                            "station_ids": ",".join(
                                map(str, ids[start : start + 1000])
                            ),
                            "page": 1,
                            "page_size": 1000,
                        },
                    )
                    for start in range(0, count, 1000)
                ]
                self.assertEqual(self.fetch.await_args_list, expected_calls)

    async def test_pagination_and_batches(self) -> None:
        items = [station(1), station(2), station(1001)]
        self.fetch.side_effect = [
            response(items[:1], total_pages=2),
            response(items[1:2], page=2, total_pages=2),
            response(items[2:]),
        ]

        result = await self.client.get_prices_bulk(list(range(1, 1002)))

        self.assertEqual(result, items)
        first_batch = ",".join(map(str, range(1, 1001)))
        self.assertEqual(
            self.fetch.await_args_list,
            [
                call(
                    Endpoint.STATIONS_BULK,
                    {"station_ids": first_batch, "page": 1, "page_size": 1000},
                ),
                call(
                    Endpoint.STATIONS_BULK,
                    {"station_ids": first_batch, "page": 2, "page_size": 1000},
                ),
                call(
                    Endpoint.STATIONS_BULK,
                    {"station_ids": "1001", "page": 1, "page_size": 1000},
                ),
            ],
        )

    async def test_omitted_stations(self) -> None:
        self.fetch.return_value = response([station(1)])
        self.assertEqual(await self.client.get_prices_bulk([1, 2]), [station(1)])

    async def test_no_matching_stations(self) -> None:
        self.fetch.return_value = response([], total_pages=0)
        self.assertEqual(await self.client.get_prices_bulk([1]), [])
        self.fetch.assert_awaited_once()

    async def test_http_errors(self) -> None:
        for status in (401, 429, 500):
            with self.subTest(status=status):
                error = ClientResponseError(Mock(), (), status=status)
                self.fetch.side_effect = error

                with self.assertRaises(ClientResponseError) as raised:
                    await self.client.get_prices_bulk([1])

                self.assertIs(raised.exception, error)

    async def test_later_request_failure(self) -> None:
        error = ClientResponseError(Mock(), (), status=500)
        for ids, first_page in (
            ([1, 2], response([station(1)], total_pages=2)),
            (list(range(1, 1002)), response([station(1)])),
        ):
            with self.subTest(station_count=len(ids)):
                self.fetch.side_effect = [first_page, error]

                with self.assertRaises(ClientResponseError) as raised:
                    await self.client.get_prices_bulk(ids)

                self.assertIs(raised.exception, error)

    async def test_single_station_method_unchanged(self) -> None:
        item = station(1234)
        self.fetch.return_value = item

        self.assertEqual(await self.client.get_prices(1234), item)
        self.fetch.assert_awaited_once_with(Endpoint.PRICES, {"station_id": 1234})


class BulkRequestTest(unittest.IsolatedAsyncioTestCase):
    """Test the bulk request through the HTTP connector."""

    async def test_request(self) -> None:
        requests = []
        items = [station(1), station(2)]

        async def handle(request: web.Request) -> web.Response:
            requests.append(request)
            return web.json_response(response(items))

        app = web.Application()
        app.router.add_get("/v1/stations/bulk", handle)
        async with TestServer(app) as server:
            with patch(
                "pybraendstofpriser.conn.API_ENDPOINT", str(server.make_url("/v1"))
            ):
                result = await Braendstofpriser("test-key").get_prices_bulk([1, 2])

        self.assertEqual(result, items)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].headers["X-API-KEY"], "test-key")
        self.assertEqual(
            dict(requests[0].query),
            {"station_ids": "1,2", "page": "1", "page_size": "1000"},
        )
