# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""PyTCL allows control EDA tools directly from Python that use TCL."""

import os
import sys
from os import PathLike
from uuid import uuid4
from time import sleep
from typing import Self
from tempfile import gettempdir
from subprocess import Popen, CalledProcessError
from multiprocessing.connection import Client, Connection
from .call import TCLCall


EXECUTE_TCL: str = os.path.join(os.path.dirname(__file__), "execute.tcl")
WINDOWS: str = "win32"


class PyTCL:
    def __init__(self, *args: str | PathLike, timeout: float = 10, **kwargs):
        """Create new instance of PyTCL.

        Args:
            args:    Tool to be executed and controlled by PyTCL.
            timeout: Timeout in seconds when waiting for started tool to connect.
            kwargs:  Additional named arguments directly passed to `subprocess.Popen`.
        """
        address: str

        if sys.platform == WINDOWS:
            address = "\\\\.\\pipe\\pytcl-" + uuid4().hex
        else:
            address = os.path.join(gettempdir(), "pytcl-" + uuid4().hex)

        # PyTCL offers some string placeholders {} that you can use:
        # {tcl}      -> it will insert <pytcl>/execute.tcl
        # {address}  -> it will insert Unix socket, Windows named pipe or network address
        cmd: list[str] = [
            str(arg).format(tcl=EXECUTE_TCL, address=address) for arg in args
        ]

        if not cmd:
            cmd = ["tclsh"]

        if EXECUTE_TCL not in cmd:
            cmd.append(EXECUTE_TCL)

        if address not in cmd:
            cmd.append(address)

        self._process: Popen = Popen(cmd, **kwargs)
        self._connection: Connection

        while True:
            try:
                self._connection = Client(address)
                return
            except FileNotFoundError as e:
                if timeout > 0:
                    sleep(0.1)
                    timeout -= 0.1
                else:
                    raise e

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if not self._connection.closed:
            self._connection.close()

        self._process.wait()

        if self._process.returncode:
            raise CalledProcessError(self._process.returncode, self._process.args)

    def __getattr__(self, name: str) -> TCLCall:
        """Call TCL procedure or evaluate expression.

        Args:
            name: Name of TCL procedure to invoke.

        Returns:
            Callable TCL object.
        """
        return TCLCall(name, self._connection)
