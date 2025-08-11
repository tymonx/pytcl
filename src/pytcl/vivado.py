# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""EDA tool: Xilinx Vivado."""

from os import PathLike
from .pytcl import PyTCL


class Vivado(PyTCL):
    """EDA tool: Xilinx Vivado."""

    def __init__(
        self,
        *args: str | PathLike,
        mode: str = "batch",
        nojournal: bool = True,
        notrace: bool = True,
        nolog: bool = True,
        **kwargs,
    ):
        """Create new instance of Xilinx Vivado.

        Args:
            args:      Additional arguments for Xilinx Vivado. Like Xilinx Vivado `*.xpr` project file.
            mode:      Xilinx Vivado mode: batch, tcl or gui.
            nojournal: Do not create a journal file.
            notrace:   Do not create a trace file.
            nolog:     Do not create a log file.
            kwargs:    Additional named arguments directly passed to `subprocess.Popen`.
        """
        cmd: list[str | PathLike] = ["vivado"]

        if nojournal:
            cmd.append("-nojournal")

        if notrace:
            cmd.append("-notrace")

        if nolog:
            cmd.append("-nolog")

        if mode:
            cmd.extend(("-mode", mode))

        cmd.extend(args)

        # PyTCL offers some placeholders like `{tcl}` to insert `<pytcl>/execute.tcl`
        # Remaining missing arguments by PyTCL are always appended at the end: `{address}`
        cmd.extend(("-source", "{tcl}", "-tclargs"))

        super().__init__(*cmd, **kwargs)
