from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET


REQUIRED_FUNCTION_BLOCKS = {
    "FB_Column",
    "FB_ColumnStateMachine",
    "FB_GravimetricFlowEstimator",
    "FB_SlowPIController",
    "FB_InputScale",
    "FB_OutputScale",
    "FB_Pump",
    "FB_TemperatureController",
    "FB_Aeration",
    "FB_Alarm",
    "FB_CommandMailbox",
    "FB_GatewayHealth",
    "FB_DataQuality",
    "FB_RecipeRuntime",
    "FB_CampaignRuntime",
    "FB_FailSafe",
}

REQUIRED_TYPES = {
    "ST_ColumnConfig",
    "ST_ColumnStatus",
    "ST_ColumnCommand",
    "ST_ColumnAlarm",
    "ST_RecipeParameters",
    "ST_GatewayStatus",
    "ST_ScaleReading",
    "ST_PumpCommand",
    "ST_DataQuality",
    "ST_SystemRuntime",
    "ST_OpcuaRuntime",
    "ST_ColumnRuntime",
    "ST_ColumnBank",
}

REQUIRED_PROGRAMS = {
    "PRG_ColumnControl",
    "PRG_Simulation",
}

REQUIRED_GLOBALS = {
    "GVL_System",
    "GVL_OPCUA",
    "GVL_Recipes",
    "GVL_Gateways",
    "GVL_Columns",
    "GVL_ColumnInstances",
    "GVL_Simulation",
}


@dataclass(frozen=True)
class CodesysSourceIndex:
    root: Path
    source_files: dict[str, str]
    function_blocks: set[str]
    types: set[str]
    programs: set[str]
    globals: set[str]


@dataclass(frozen=True)
class CodesysValidation:
    missing_function_blocks: tuple[str, ...]
    missing_types: tuple[str, ...]
    missing_programs: tuple[str, ...]
    missing_globals: tuple[str, ...]
    supports_200_columns: bool
    real_io_default_false: bool

    @property
    def ok(self) -> bool:
        return not (
            self.missing_function_blocks
            or self.missing_types
            or self.missing_programs
            or self.missing_globals
            or not self.supports_200_columns
            or not self.real_io_default_false
        )


def _read_st_sources(codesys_control_root: Path) -> dict[str, str]:
    src_root = codesys_control_root / "src"
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(src_root.glob("*.st"))
    }


def index_codesys_sources(codesys_control_root: str | Path) -> CodesysSourceIndex:
    root = Path(codesys_control_root)
    source_files = _read_st_sources(root)
    joined = "\n".join(source_files.values())

    function_blocks = set(re.findall(r"\bFUNCTION_BLOCK\s+([A-Za-z_][A-Za-z0-9_]*)", joined))
    types = set(re.findall(r"\bTYPE\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", joined))
    programs = set(re.findall(r"\bPROGRAM\s+([A-Za-z_][A-Za-z0-9_]*)", joined))

    globals_found: set[str] = set()
    for global_name in REQUIRED_GLOBALS:
        if re.search(rf"\b{re.escape(global_name)}\b\s*:", joined):
            globals_found.add(global_name)

    return CodesysSourceIndex(
        root=root,
        source_files=source_files,
        function_blocks=function_blocks,
        types=types,
        programs=programs,
        globals=globals_found,
    )


def validate_codesys_sources(codesys_control_root: str | Path) -> CodesysValidation:
    index = index_codesys_sources(codesys_control_root)
    joined = "\n".join(index.source_files.values())

    supports_200_columns = bool(
        re.search(r"Columns\s*:\s*ARRAY\[1\.\.200\]\s+OF\s+ST_ColumnRuntime", joined)
        and re.search(r"GVL_ColumnInstances\s*:\s*ARRAY\[1\.\.200\]\s+OF\s+FB_Column", joined)
        and re.search(r"FOR\s+ColumnIndex\s*:=\s*1\s+TO\s+200\s+DO", joined)
    )
    real_io_default_false = bool(re.search(r"RealIoEnabled\s*:=\s*FALSE", joined))

    return CodesysValidation(
        missing_function_blocks=tuple(sorted(REQUIRED_FUNCTION_BLOCKS - index.function_blocks)),
        missing_types=tuple(sorted(REQUIRED_TYPES - index.types)),
        missing_programs=tuple(sorted(REQUIRED_PROGRAMS - index.programs)),
        missing_globals=tuple(sorted(REQUIRED_GLOBALS - index.globals)),
        supports_200_columns=supports_200_columns,
        real_io_default_false=real_io_default_false,
    )


def build_plcopen_xml(codesys_control_root: str | Path, project_name: str = "codesys-opcua-interface") -> ET.ElementTree:
    index = index_codesys_sources(codesys_control_root)
    root = ET.Element("plcopenSource", {"project": project_name, "profile": "preliminary-st-source"})
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "note").text = (
        "Preliminary PLCopen-style source export. Validate/import in CODESYS Development System "
        "before using with a real runtime."
    )

    declarations = ET.SubElement(root, "declarations")
    for type_name in sorted(index.types):
        ET.SubElement(declarations, "type", {"name": type_name})
    for fb_name in sorted(index.function_blocks):
        ET.SubElement(declarations, "functionBlock", {"name": fb_name})
    for program_name in sorted(index.programs):
        ET.SubElement(declarations, "program", {"name": program_name})

    sources = ET.SubElement(root, "sources")
    for file_name, source in index.source_files.items():
        file_el = ET.SubElement(sources, "source", {"path": f"src/{file_name}", "language": "st"})
        file_el.text = source

    return ET.ElementTree(root)


def write_plcopen_xml(codesys_control_root: str | Path, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tree = build_plcopen_xml(codesys_control_root)
    ET.indent(tree, space="  ")
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output
