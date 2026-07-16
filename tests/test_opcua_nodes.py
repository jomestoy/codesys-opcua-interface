import pytest

from codesys_opcua_interface.opcua_nodes import COLUMN_NODES, COMMAND_NODES, SYSTEM_NODES, command_mailbox_symbol


def test_column_symbols_require_column_id_and_never_embed_namespace_index():
    symbol = COLUMN_NODES["input_weight_kg"].symbol(7)

    assert symbol == "GVL_Columns.Columns[007].Status.InputScale.WeightKg"
    assert not symbol.startswith("ns=")

    with pytest.raises(ValueError):
        COLUMN_NODES["input_weight_kg"].symbol()


def test_system_and_command_symbols_are_global():
    assert SYSTEM_NODES["is_active"].symbol() == "GVL_System.IsActive"
    assert COMMAND_NODES["confirmation"].symbol() == "GVL_OPCUA.CommandConfirmation"
    assert command_mailbox_symbol() == "GVL_OPCUA.CommandMailbox"
