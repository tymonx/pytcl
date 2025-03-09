# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Receive data from Unix file socket and print it to standard output (stdout)."""

import sys
from multiprocessing.connection import Listener


def main():
    """Main entrypoint."""
    with Listener(sys.argv[1]) as listener:
        with listener.accept() as connection:
            while True:
                try:
                    print(connection.recv(), flush=True)
                except EOFError:
                    return


if __name__ == "__main__":
    main()
