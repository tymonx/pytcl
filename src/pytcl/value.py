# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""TCL value abstraction type for TCL string, list, dict, integer, boolean, floating point."""

from typing import Any, Tuple
from collections.abc import Iterable, Iterator


class TCLValue:
    def __init__(self, value: Any):
        """Create new instalce of TCL value from provided string that can be anything.

        Args:
            value: Any TCL value. Anything in TCL is a string.
        """
        self._value: str = str(value)

    def __str__(self) -> str:
        return self._value

    def __bool__(self) -> bool:
        return bool(self._value)

    def __int__(self) -> int:
        return int(self._value)

    def __float__(self) -> float:
        return float(self._value)

    def __iter__(self) -> Iterator["TCLValue"]:
        return iter(TCLValue(value) for value in self._value.split())

    def __len__(self) -> int:
        """Number of elements in TCL list."""
        return len(self._value.split())

    def __contains__(self, item: Any) -> bool:
        """Check if provided item is part of TCL value."""
        return str(item) in self._value

    def __getitem__(self, key: str | int) -> "TCLValue":
        """Get single TCL value from TCL list or dictionary using provided index or dictionary key."""
        if isinstance(key, int):
            return list(self.__iter__())[key]

        return dict(self.items())[str(key)]

    def items(self) -> Iterable[Tuple[str, "TCLValue"]]:
        items: list[str] = self._value.split()
        return zip(items[0::2], (TCLValue(item) for item in items[1::2]))

    def keys(self) -> list[str]:
        """List of dictionary keys."""
        return self._value.split()[0::2]

    def values(self) -> list["TCLValue"]:
        """List of dictionary values."""
        return [TCLValue(item) for item in self._value.split()[1::2]]
