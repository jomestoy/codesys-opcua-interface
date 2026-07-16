from pathlib import Path
import xml.etree.ElementTree as ET

from codesys_opcua_interface.codesys_project import (
    REQUIRED_FUNCTION_BLOCKS,
    REQUIRED_TYPES,
    build_plcopen_xml,
    index_codesys_sources,
    validate_codesys_sources,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CODESYS_ROOT = REPO_ROOT / "codesys-control"


def test_codesys_sources_define_required_types_and_function_blocks():
    index = index_codesys_sources(CODESYS_ROOT)

    assert REQUIRED_FUNCTION_BLOCKS <= index.function_blocks
    assert REQUIRED_TYPES <= index.types


def test_codesys_sources_support_200_reusable_column_instances():
    validation = validate_codesys_sources(CODESYS_ROOT)

    assert validation.ok, validation
    assert validation.supports_200_columns
    assert validation.real_io_default_false


def test_main_program_routes_opcua_mailbox_through_codesys_authority():
    program = (CODESYS_ROOT / "src" / "PRG_ColumnControl.st").read_text(encoding="utf-8")

    assert "FOR ColumnIndex := 1 TO 200 DO" in program
    assert "GVL_OPCUA.CommandMailbox.Status = Pending" in program
    assert "NOT GVL_System.IsActive" in program
    assert "GVL_OPCUA.CommandConfirmation" in program
    assert "GVL_ColumnInstances[ColumnIndex]" in program


def test_simulation_program_refuses_to_run_with_real_io_enabled():
    simulation = (CODESYS_ROOT / "src" / "PRG_Simulation.st").read_text(encoding="utf-8")

    assert "GVL_System.RealIoEnabled" in simulation
    assert "RETURN;" in simulation
    assert "FOR ColumnIndex := 1 TO 200 DO" in simulation


def test_plcopen_builder_produces_parseable_source_manifest():
    tree = build_plcopen_xml(CODESYS_ROOT)
    xml_text = ET.tostring(tree.getroot(), encoding="unicode")

    assert "FB_Column" in xml_text
    assert "PRG_ColumnControl" in xml_text
    assert "preliminary-st-source" in xml_text
    ET.fromstring(xml_text)
