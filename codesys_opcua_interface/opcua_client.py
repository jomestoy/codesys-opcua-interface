from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


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
    connect_timeout_s: float = 5.0
    request_timeout_s: float = 5.0


@dataclass(frozen=True)
class OpcuaDataValue:
    symbol: str
    value: Any
    quality: str = "Good"
    source_timestamp: str | None = None
    server_timestamp: str | None = None


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

    def __init__(self, config: OpcuaEndpointConfig, client_factory: Callable[[str], Any] | None = None) -> None:
        self.config = config
        self.client: Any | None = None
        self.namespace_index: int | None = None
        self._client_factory = client_factory

    @property
    def endpoint_url(self) -> str:
        return self.config.endpoint_url

    async def connect(self) -> None:
        if not self.config.endpoint_url.startswith("opc.tcp://"):
            raise ValueError("endpoint_url debe usar opc.tcp://")
        if self.config.security.security_mode != "SignAndEncrypt":
            raise ValueError("security_mode debe ser SignAndEncrypt")
        if self._client_factory is None:
            try:
                from asyncua import Client  # type: ignore
            except ImportError as exc:
                raise RuntimeError("asyncua no instalado; ejecutar pip install -e .[opcua] para OPC UA real") from exc
            self.client = Client(url=self.config.endpoint_url, timeout=self.config.request_timeout_s)
        else:
            self.client = self._client_factory(self.config.endpoint_url)
        if self.config.security.security_mode != "SignAndEncrypt":
            raise ValueError("security_mode debe ser SignAndEncrypt")
        await self._configure_security_if_available()
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

    async def read_data_value(self, symbol: str) -> OpcuaDataValue:
        if self.client is None:
            raise RuntimeError("cliente OPC UA no conectado")
        node = self.client.get_node(self.node_id(symbol))
        if hasattr(node, "read_data_value"):
            data = await node.read_data_value()
            value = getattr(getattr(data, "Value", None), "Value", None)
            status = str(getattr(data, "StatusCode", "Good"))
            source_ts = getattr(data, "SourceTimestamp", None)
            server_ts = getattr(data, "ServerTimestamp", None)
            return OpcuaDataValue(symbol, value, status, str(source_ts) if source_ts else None, str(server_ts) if server_ts else None)
        return OpcuaDataValue(symbol, await node.read_value())

    async def read_many(self, symbols: list[str]) -> dict[str, Any]:
        return {symbol: await self.read_value(symbol) for symbol in symbols}

    async def write_value(self, symbol: str, value: Any) -> None:
        if self.client is None:
            raise RuntimeError("cliente OPC UA no conectado")
        await self.client.get_node(self.node_id(symbol)).write_value(value)

    async def subscribe(self, symbols: list[str], callback: Callable[[str, Any], Awaitable[None] | None], publishing_interval_ms: int = 1000) -> Any:
        if self.client is None:
            raise RuntimeError("cliente OPC UA no conectado")

        class Handler:
            def datachange_notification(self, node: Any, value: Any, data: Any) -> None:
                node_id = str(node)
                result = callback(node_id, value)
                if hasattr(result, "__await__"):
                    # asyncua accepts sync handlers; callers needing async side effects
                    # should enqueue externally. We intentionally do not run loops here.
                    return None
                return None

        subscription = await self.client.create_subscription(publishing_interval_ms, Handler())
        nodes = [self.client.get_node(self.node_id(symbol)) for symbol in symbols]
        return await subscription.subscribe_data_change(nodes)

    async def _configure_security_if_available(self) -> None:
        if self.client is None:
            return
        security = self.config.security
        if not security.certificate_path or not security.private_key_path:
            return
        if hasattr(self.client, "set_security_string"):
            policy = security.security_policy
            mode = security.security_mode
            result = self.client.set_security_string(f"{policy},{mode},{security.certificate_path},{security.private_key_path}")
            if hasattr(result, "__await__"):
                await result
