"""Tests for the User-Agent sent by the client."""

import unittest
from importlib.metadata import PackageNotFoundError, version
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestServer

from pybraendstofpriser import Braendstofpriser
from pybraendstofpriser.conn import _default_user_agent


class UserAgentTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        try:
            self.installed_version = version("pybraendstofpriser")
        except PackageNotFoundError:
            self.installed_version = "unknown"

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

    async def test_default_uses_version_resolved_at_import(self) -> None:
        with patch("pybraendstofpriser.conn.version") as lookup:
            client = Braendstofpriser("test-key")
            await client.list_companies()
            lookup.assert_not_called()

        self.assertEqual(self.user_agents, [f"pybraendstofpriser/{self.installed_version}"])

    async def test_custom_value_overrides_default(self) -> None:
        client = Braendstofpriser("test-key", user_agent="MyApp/1.0")
        await client.list_companies()
        self.assertEqual(self.user_agents, ["MyApp/1.0"])


class DefaultUserAgentTest(unittest.TestCase):
    def test_missing_metadata_uses_unknown_version(self) -> None:
        with patch("pybraendstofpriser.conn.version", side_effect=PackageNotFoundError):
            self.assertEqual(_default_user_agent(), "pybraendstofpriser/unknown")
