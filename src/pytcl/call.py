# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Call TCL expression from Python."""

import re
import json
from typing import Any, Tuple
from collections.abc import Iterable, Sequence, Mapping
from multiprocessing.connection import Connection
from .value import TCLValue
from .error import TCLError


# TCL loves to use whitespace characters as separators
WHITESPACE = re.compile(r"\s")


class TCLCall:
    """Call TCL expression from Python."""

    def __init__(self, name: str, rx: Connection, tx: Connection):
        """Create new instances of TCL call.

        Args:
            name: Name of TCL procedure.
            rx:   Connection from Python to TCL.
            tx:   Connection from TCL to Python.
        """
        self._name: str = name
        self._rx: Connection = rx
        self._tx: Connection = tx

    def __call__(self, *args: Any, check: bool = True, **kwargs) -> TCLValue:
        """Call TCL procedure.

        Args:
            args:  Arguments of TCL procedure.
            check: If True, raise an exception `TCLError` if TCL execution failed.

        Returns:
            TCL value: string, list, dict, boolean, integer, floating point.
        """
        cmd: list[str] = [self._name] + [self._cast(arg) for arg in args]
        self._rx.send(" ".join(cmd))

        data: dict[str, Any] = json.loads(self._tx.recv())
        result: str = data.get("result", "")
        status: int = data.get("status", 0)

        if check and status:
            raise TCLError(status, cmd, result)

        return TCLValue(result)

    def __str__(self) -> str:
        """Convert TCL value to Python string type."""
        return self.__call__().__str__()

    def __int__(self) -> int:
        """Convert TCL value to Python integer type."""
        return self.__call__().__int__()

    def __float__(self) -> float:
        """Convert TCL value to Python floating point type."""
        return self.__call__().__float__()

    def __bool__(self) -> bool:
        """Convert TCL value to Python boolean type."""
        return self.__call__().__bool__()

    def __iter__(self):
        """Iterator over TCL list. Used to convert TCL value to Python list or sequence type."""
        return self.__call__().__iter__()

    def __getitem__(self, key: str) -> TCLValue:
        """Get single TCL value from TCL dictionary using provided dictionary key."""
        return self.__call__().__getitem__(key)

    def items(self) -> Iterable[Tuple[str, TCLValue]]:
        """List of TCL dictionary items as pair of key string and TCL value."""
        return self.__call__().items()

    @staticmethod
    def _cast(value: Any) -> str:
        """Cast Python value to TCL value.

        Args:
            value: Any Python value.

        Returns:
            TCL value as string that can be string, list, dict, boolean, integer, floating point.
        """
        if isinstance(value, str):
            return value if value and not WHITESPACE.search(value) else f"{{{value}}}"

        if isinstance(value, bool):
            return str(int(value))

        if isinstance(value, Sequence):
            return TCLCall._cast(" ".join(TCLCall._cast(item) for item in value))

        if isinstance(value, Mapping):
            return TCLCall._cast(
                " ".join(key + " " + TCLCall._cast(item) for key, item in value.items())
            )

        return TCLCall._cast(str(value))
