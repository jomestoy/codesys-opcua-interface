from datetime import datetime, timedelta, timezone

import pytest

from codesys_opcua_interface.command_model import ColumnCommand, CommandMailbox, CommandStatus
from codesys_opcua_interface.redundancy import RedundantCodesysSimulator


def test_command_mailbox_enforces_ttl_and_idempotency():
    mailbox = CommandMailbox()
    command = mailbox.submit(ColumnCommand(column_id=1, command_type="set_flow", requested_value=50, requested_by="qa"), idempotency_key="same")
    repeated = mailbox.submit(ColumnCommand(column_id=1, command_type="set_flow", requested_value=60, requested_by="qa"), idempotency_key="same")

    assert repeated.command_id == command.command_id

    expired = mailbox.expire(command.requested_at + timedelta(seconds=31))

    assert expired[0].status == CommandStatus.EXPIRED


def test_command_mailbox_rejects_out_of_range_setpoint():
    mailbox = CommandMailbox()
    with pytest.raises(ValueError):
        mailbox.submit(ColumnCommand(column_id=1, command_type="set_flow", requested_value=101, requested_by="qa"))


def test_redundant_simulator_writes_only_to_active_endpoint():
    simulator = RedundantCodesysSimulator("opc.tcp://a:4840", "opc.tcp://b:4840")
    first = simulator.submit_command(ColumnCommand(column_id=1, command_type="start", requested_by="qa"))
    simulator.fail_primary()
    second = simulator.submit_command(ColumnCommand(column_id=2, command_type="pause", requested_by="qa"))

    assert first.status == CommandStatus.APPLIED
    assert "CODESYS-A" in first.result
    assert second.status == CommandStatus.APPLIED
    assert "CODESYS-B" in second.result
    assert simulator.status()["double_write_prevented"] is True
