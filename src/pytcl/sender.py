# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Send data to Unix file socket from standard input (stdin)."""

import sys
from multiprocessing.connection import Client


def main():
    """Main entrypoint."""
    with Client(sys.argv[1]) as connection:
        for line in sys.stdin:
            connection.send(line.strip())


if __name__ == "__main__":
    main()
