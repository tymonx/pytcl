# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Test PyTCL with Xilinx Vivado."""

from shutil import which
from pathlib import Path
from pytcl import Vivado, PyTCL
import pytest

pytestmark = pytest.mark.skipif(not which("vivado"), reason="Requires Xilinx Vivado")


def test_vivado_create_project(tmp_path: Path) -> None:
    """Test Xilinx Vivado: create_project example <project-dir>."""
    with Vivado(cwd=tmp_path) as vivado:
        vivado.create_project("example", tmp_path)
        vivado.close_project()

    assert (tmp_path / "example.xpr").exists()


def test_vivado_directly_with_pytcl(tmp_path: Path) -> None:
    """Test Xilinx Vivado: create_project example <project-dir>."""
    # PyTCL offers some placeholders like `{tcl}` to insert `<pytcl/>executa.tcl`
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
