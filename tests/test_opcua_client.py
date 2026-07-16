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
