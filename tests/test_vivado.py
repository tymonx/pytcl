# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Test PyTCL with Xilinx Vivado."""

from shutil import which
from pathlib import Path
from pytcl import Vivado
import pytest

pytestmark = pytest.mark.skipif(not which("vivado"), reason="Requires Xilinx Vivado")


def test_vivado_create_project(tmp_path: Path) -> None:
    """Test Xilinx Vivado: create_project example <project-dir>."""
    with Vivado() as vivado:
        vivado.create_project("example", tmp_path)
        vivado.close_project()

    assert (tmp_path / "example.xpr").exists()
