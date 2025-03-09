# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""TCL errors."""

from subprocess import CalledProcessError


class TCLError(CalledProcessError):
    """TCL error."""

    def __init__(self, returncode: int, cmd: list[str], output: str):
        """Create new instance of TCL error.

        Args:
            returncode: TCL status code returned from TCL `catch` when evaluating requested TCL expression `cmd`.
            cmd:        Evaluated TCL expression by TCL `eval`.
            output:     TCL result returned from TCL `catch` when evaluating requested TCL expression `cmd`.
        """
        super().__init__(returncode, cmd, output)

    def __str__(self) -> str:
        """TCL error message."""
        return f"'{' '.join(self.cmd)}' returned non-zero status {self.returncode}: {self.output}"
