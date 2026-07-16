import asyncio

import pytest

from codesys_opcua_interface.command_model import ColumnCommand, CommandStatus
from codesys_opcua_interface.opcua_connector import CodesysOpcuaConnector, RedundancyError
from codesys_opcua_interface.opcua_nodes import COLUMN_NODES
from codesys_opcua_interface.opcua_simulator import SimulatedOpcuaEndpoint


def test_connector_writes_command_only_to_active_endpoint():
    async def run():
        primary = SimulatedOpcuaEndpoint("opc.tcp://a:4840", controller_id="A", is_active=True)
        secondary = SimulatedOpcuaEndpoint("opc.tcp://b:4840", controller_id="B", controller_role="secondary", is_active=False)
        connector = CodesysOpcuaConnector(primary, secondary)

        command = await connector.submit_command(ColumnCommand(column_id=1, command_type="set_flow", requested_value=50.0, requested_by="qa"))

        assert command.status == CommandStatus.APPLIED
        assert "A" in command.result
        assert len(primary.writes) == 1
        assert secondary.writes == []

    asyncio.run(run())


def test_connector_rejects_double_active_to_prevent_double_write():
    async def run():
        primary = SimulatedOpcuaEndpoint("opc.tcp://a:4840", controller_id="A", is_active=True)
        secondary = SimulatedOpcuaEndpoint("opc.tcp://b:4840", controller_id="B", controller_role="secondary", is_active=True)
        connector = CodesysOpcuaConnector(primary, secondary)

        with pytest.raises(RedundancyError):
            await connector.submit_command(ColumnCommand(column_id=1, command_type="start", requested_by="qa"))

    asyncio.run(run())


def test_connector_uses_secondary_after_primary_offline():
    async def run():
        primary = SimulatedOpcuaEndpoint("opc.tcp://a:4840", controller_id="A", is_active=False, online=False)
        secondary = SimulatedOpcuaEndpoint("opc.tcp://b:4840", controller_id="B", controller_role="secondary", is_active=True)
        connector = CodesysOpcuaConnector(primary, secondary)

        command = await connector.submit_command(ColumnCommand(column_id=2, command_type="pause", requested_by="qa"))

        assert command.status == CommandStatus.APPLIED
        assert "B" in command.result
        assert len(secondary.writes) == 1

    asyncio.run(run())


def test_connector_subscribes_to_active_endpoint_symbols():
    async def run():
        primary = SimulatedOpcuaEndpoint("opc.tcp://a:4840", is_active=True)
        secondary = SimulatedOpcuaEndpoint("opc.tcp://b:4840", controller_role="secondary", is_active=False)
        connector = CodesysOpcuaConnector(primary, secondary)
        symbol = COLUMN_NODES["flow_measured_kg_h"].symbol(1)

        handles = await connector.subscribe_status([symbol], lambda node, value: None)

        assert handles == [f"ns=4;s={symbol}"]

    asyncio.run(run())
