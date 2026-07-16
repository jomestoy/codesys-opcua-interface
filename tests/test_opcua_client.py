import asyncio

import pytest

from codesys_opcua_interface.opcua_client import (
    AsyncuaCodesysClient,
    OpcuaEndpointConfig,
    OpcuaSecurityConfig,
    build_string_node_id,
)


def test_node_id_uses_resolved_namespace_index():
    assert build_string_node_id(4, "GVL_System.Heartbeat") == "ns=4;s=GVL_System.Heartbeat"


def test_opcua_client_requires_connection_before_node_id():
    client = AsyncuaCodesysClient(OpcuaEndpointConfig("opc.tcp://demo:4840", "urn:demo", OpcuaSecurityConfig()))

    with pytest.raises(RuntimeError):
        client.node_id("GVL_System.Heartbeat")


def test_opcua_client_supports_injected_fake_client():
    async def run():
        class FakeNode:
            def __init__(self) -> None:
                self.value = None

            async def read_value(self):
                return self.value

            async def write_value(self, value):
                self.value = value

        class FakeClient:
            def __init__(self, url: str) -> None:
                self.url = url
                self.node = FakeNode()

            async def connect(self) -> None:
                return None

            async def disconnect(self) -> None:
                return None

            async def get_namespace_index(self, uri: str) -> int:
                return 9

            def get_node(self, node_id: str):
                assert node_id == "ns=9;s=GVL_System.Heartbeat"
                return self.node

        client = AsyncuaCodesysClient(
            OpcuaEndpointConfig("opc.tcp://demo:4840", "urn:demo", OpcuaSecurityConfig()),
            client_factory=FakeClient,
        )

        await client.connect()
        await client.write_value("GVL_System.Heartbeat", 123)

        assert client.endpoint_url == "opc.tcp://demo:4840"
        assert await client.read_value("GVL_System.Heartbeat") == 123

    asyncio.run(run())
