from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OpcuaSecurityConfig:
    security_policy: str = "Basic256Sha256"
    security_mode: str = "SignAndEncrypt"
    certificate_path: str | None = None
    private_key_path: str | None = None
    trust_list_path: str | None = None


@dataclass
class OpcuaEndpointConfig:
    endpoint_url: str
    namespace_uri: str
    security: OpcuaSecurityConfig


def build_string_node_id(namespace_index: int, symbol: str) -> str:
    if namespace_index < 0:
        raise ValueError("namespace_index invalido")
    if not symbol:
        raise ValueError("symbol requerido")
    return f"ns={namespace_index};s={symbol}"


class AsyncuaCodesysClient:
    """OPC UA client wrapper.

    This class is intentionally lazy-imported. Unit tests and offline demo do
    not require network access or asyncua. Real OPC UA validation requires
    installing `codesys-opcua-interface[opcua]`, certificates and a CODESYS
    runtime.
    """

    def __init__(self, config: OpcuaEndpointConfig) -> None:
        self.config = config
        self.client: Any | None = None
        self.namespace_index: int | None = None

    async def connect(self) -> None:
        try:
            from asyncua import Client  # type: ignore
        except ImportError as exc:
            raise RuntimeError("asyncua no instalado; ejecutar pip install -e .[opcua] para OPC UA real") from exc
        if not self.config.endpoint_url.startswith("opc.tcp://"):
            raise ValueError("endpoint_url debe usar opc.tcp://")
        self.client = Client(url=self.config.endpoint_url)
        if self.config.security.security_mode != "SignAndEncrypt":
            raise ValueError("security_mode debe ser SignAndEncrypt")
        await self.client.connect()
        self.namespace_index = await self.client.get_namespace_index(self.config.namespace_uri)

    async def disconnect(self) -> None:
        if self.client is not None:
            await self.client.disconnect()
        self.client = None

    def node_id(self, symbol: str) -> str:
        if self.namespace_index is None:
            raise RuntimeError("cliente OPC UA no conectado o namespace no resuelto")
        return build_string_node_id(self.namespace_index, symbol)

    async def read_value(self, symbol: str) -> Any:
        if self.client is None:
            raise RuntimeError("cliente OPC UA no conectado")
        return await self.client.get_node(self.node_id(symbol)).read_value()

    async def write_value(self, symbol: str, value: Any) -> None:
        if self.client is None:
            raise RuntimeError("cliente OPC UA no conectado")
        await self.client.get_node(self.node_id(symbol)).write_value(value)
