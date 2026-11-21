"""Tests for the User-Agent sent by the client."""

import unittest
from importlib.metadata import PackageNotFoundError
from threading import get_ident
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestServer

from pybraendstofpriser import Braendstofpriser


class UserAgentTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.user_agents = []

        async def record_request(request: web.Request) -> web.Response:
            self.user_agents.append(request.headers["User-Agent"])
            return web.json_response([])

        app = web.Application()
        app.router.add_get("/companies", record_request)
        server = TestServer(app)
        await server.start_server()
        self.addAsyncCleanup(server.close)
        endpoint = str(server.make_url("/")).rstrip("/")
        self.enterContext(patch("pybraendstofpriser.conn.API_ENDPOINT", endpoint))

    async def test_default_resolves_version_off_the_event_loop(self) -> None:
        event_loop_thread = get_ident()
        installed_version = "9.8.7"

        def read_version(_package: str) -> str:
            self.assertNotEqual(get_ident(), event_loop_thread)
            return installed_version

        with patch(
            "pybraendstofpriser.conn.version", side_effect=read_version
        ) as version:
            client = Braendstofpriser("test-key")
            version.assert_not_called()
            await client.list_companies()
            await client.list_companies()
            version.assert_called_once_with("pybraendstofpriser")

        self.assertEqual(self.user_agents, [f"pybraendstofpriser/{installed_version}"] * 2)

    async def test_custom_value_skips_version_lookup(self) -> None:
        with patch("pybraendstofpriser.conn.version") as version:
            client = Braendstofpriser("test-key", user_agent="MyApp/1.0")
            await client.list_companies()
            version.assert_not_called()

        self.assertEqual(self.user_agents, ["MyApp/1.0"])

    async def test_missing_metadata_uses_unknown_version(self) -> None:
        with patch("pybraendstofpriser.conn.version", side_effect=PackageNotFoundError):
            await Braendstofpriser("test-key").list_companies()

        self.assertEqual(self.user_agents, ["pybraendstofpriser/unknown"])
