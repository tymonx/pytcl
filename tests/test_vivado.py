# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Test PyTCL with Xilinx Vivado."""

from shutil import which
from pathlib import Path
from pytcl import Vivado, PyTCL
import pytest

HDL: Path = Path(__file__).parent.resolve() / "hdl"
pytestmark = pytest.mark.skipif(not which("vivado"), reason="Requires Xilinx Vivado")


def test_vivado_create_project(tmp_path: Path) -> None:
    """Test Xilinx Vivado using pytcl.Vivado helper class: create_project example <project-dir>."""
    with Vivado(cwd=tmp_path) as vivado:
        vivado.create_project("example", tmp_path)
        vivado.close_project()

    assert (tmp_path / "example.xpr").exists()


def test_vivado_directly_with_pytcl(tmp_path: Path) -> None:
    """Test Xilinx Vivado using directly pytcl.PyTCL class: create_project example <project-dir>."""
    # PyTCL offers some placeholders like `{tcl}` to insert `<pytcl/>execute.tcl`
    cmd: list[str] = [
        "vivado",
        "-nojournal",
        "-notrace",
        "-nolog",
        "-mode",
        "batch",
        "-source",
        "{tcl}",
        "-tclargs",
        "{receiver}",
        "{rx}",
        "{sender}",
        "{tx}",
    ]

    with PyTCL(*cmd, cwd=tmp_path) as vivado:
        vivado.create_project("example", tmp_path)
        vivado.close_project()

    assert (tmp_path / "example.xpr").exists()


def test_vivado_project_mode(tmp_path: Path) -> None:
    """Test Xilinx Vivado in project mode."""
    with Vivado(cwd=tmp_path) as vivado:
        vivado.create_project("example", tmp_path)
        vivado.add_files(HDL / "dut.sv")

        synthesis_runs = list(vivado.get_runs("synth_*"))
        implementation_runs = list(vivado.get_runs("impl_*"))

        vivado.launch_runs(synthesis_runs)

        # wait_on_runs was introduced in Vivado 2021.2. For backward compatibility we will use wait_on_run
        # https://docs.amd.com/r/2021.2-English/ug835-vivado-tcl-commands/wait_on_runs
        # Vivado >= 2021.2 can just use: vivado.wait_on_runs(synthesis_runs)
        for run in synthesis_runs:
            vivado.wait_on_run(run)

        vivado.launch_runs(implementation_runs)

        for run in implementation_runs:
            vivado.wait_on_run(run)

        vivado.close_project()

    assert (tmp_path / "example.xpr").exists()
