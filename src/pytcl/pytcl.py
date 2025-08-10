# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""PyTCL allows control EDA tools directly from Python that use TCL."""

import sys
from uuid import uuid4
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
WINDOWS: str = "win32"


class PyTCL:
    def __init__(self, *args: str | Path, timeout: float = 10, **kwargs):
        """Create new instance of PyTCL.

        Args:
            args:    Tool to be executed and controlled by PyTCL.
            timeout: Timeout in seconds when waiting for started tool to connect.
            kwargs:  Additional named arguments directly passed to `subprocess.Popen`.
        """
        self._dir: Path | None = None
        rx: str = ""
        tx: str = ""

        if sys.platform == WINDOWS:
            uuid: str = uuid4().hex
            rx = f"\\\\.\\pipe\\pytcl-{uuid}-rx"
            tx = f"\\\\.\\pipe\\pytcl-{uuid}-tx"
        else:
            self._dir = Path(mkdtemp(prefix="pytcl-")).resolve()
            rx = str(self._dir / "rx.sock")
            tx = str(self._dir / "tx.sock")

        # PyTCL offers some string placeholders {} that you can use:
        # {tcl}      -> it will insert <pytcl>/execute.tcl
        # {receiver} -> it will insert <pytcl>/receiver.tcl
        # {rx}       -> it will insert /tmp/pytcl-XXXXX/rx.sock
        # {sender}   -> it will insert <pytcl>/sender.tcl
        # {tx}       -> it will insert /tmp/pytcl-XXXXX/tx.sock
        # {args}     -> it will insert '{receier} {rx} {sender} {tx}' in one go
        cmd: list[str] = [
            str(arg).format(
                tcl=EXECUTE_TCL,
                receiver=RECEIVER_PY,
                rx=rx,
                sender=SENDER_PY,
                tx=tx,
                args=" ".join((str(RECEIVER_PY), rx, str(SENDER_PY), tx)),
            )
            for arg in args
        ]

        if not cmd:
            cmd = ["tclsh"]

        for item in (EXECUTE_TCL, RECEIVER_PY, rx, SENDER_PY, tx):
            if not self._in_cmd(item, cmd):
                cmd.append(str(item))

        self._listener: Listener = Listener(str(tx))
        self._process: Popen = Popen(cmd, **kwargs)
        self._tx: Connection = self._listener.accept()
        self._rx: Connection

        while True:
            try:
                self._rx = Client(rx)
                break
            except FileNotFoundError as e:
                if timeout > 0:
                    sleep(0.1)
                    timeout -= 0.1
                else:
                    raise e

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if not self._rx.closed:
            self._rx.close()

        if not self._tx.closed:
            self._tx.close()

        self._listener.close()
        self._process.wait()

        if self._dir:
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

    @staticmethod
    def _in_cmd(item: str | Path, cmd: list[str]) -> bool:
        """Check if provided item is already part of command list."""
        for argument in cmd:
            if str(item).strip() in argument:
                return True

        return False
