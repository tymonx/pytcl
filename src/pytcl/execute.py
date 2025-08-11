# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Execute commands remotely via Unix socket, Windows named pipe or network address."""

import sys
from multiprocessing.connection import Listener


def main():
    """Main entrypoint."""
    with Listener(sys.argv[1]) as listener:
        with listener.accept() as connection:
            while True:
                try:
                    print(connection.recv(), flush=True)
                    connection.send(sys.stdin.readline().strip())
                except EOFError:
                    return


if __name__ == "__main__":
    main()
