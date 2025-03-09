# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""PyTCL allows control EDA tools directly from Python that use TCL."""

from time import sleep
from typing import Self
from pathlib import Path
from tempfile import mkdtemp
from subprocess import Popen, CalledProcessError
from multiprocessing.connection import Listener, Client, Connection
from .call import TCLCall


DIR: Path = Path(__file__).parent.resolve()
EXECUTE_TCL: Path = DIR / "execute.tcl"
RECEIVER_PY: Path = DIR / "receiver.py"
SENDER_PY: Path = DIR / "sender.py"


class PyTCL:
    def __init__(self, *args: str | Path, timeout: float = 10, **kwargs):
        """Create new instance of PyTCL.

        Args:
            args:    Tool to be executed and controlled by PyTCL.
            timeout: Timeout in seconds when waiting for started tool to connect.
            kwargs:  Additional named arguments directly passed to `subprocess.Popen`.
        """
        self._dir: Path = Path(mkdtemp(prefix="pytcl-")).resolve()
        rx: Path = self._dir / "rx.sock"
        tx: Path = self._dir / "tx.sock"

        cmd: list[str] = [
            str(arg).format(
                tcl=EXECUTE_TCL,
                receiver=RECEIVER_PY,
                rx=rx,
                sender=SENDER_PY,
                tx=tx,
            )
            for arg in args
        ]

        if not cmd:
            cmd = ["tclsh"]

        for item in (EXECUTE_TCL, RECEIVER_PY, rx, SENDER_PY, tx):
            if str(item) not in cmd:
                cmd.append(str(item))

        self._listener: Listener = Listener(str(tx))
        self._process: Popen = Popen(cmd, **kwargs)
        self._tx: Connection = self._listener.accept()

        while not rx.exists() and timeout > 0:
            sleep(0.1)
            timeout -= 0.1

        self._rx: Connection = Client(str(rx))

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if not self._rx.closed:
            self._rx.close()

        if not self._tx.closed:
            self._tx.close()

        self._listener.close()
        self._process.wait()
        self._dir.rmdir()

        if self._process.returncode:
            raise CalledProcessError(self._process.returncode, self._process.args)

    def __getattr__(self, name: str) -> TCLCall:
        """Call TCL procedure or evaluate expression.

        Args:
            name: Name of TCL procedure to invoke.

        Returns:
            Callable TCL object.
        """
        return TCLCall(name, self._rx, self._tx)
