#!/usr/bin/env tclsh
# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

# Execution flow:
# PyTCL.send() -> rx.sock -> receiver.py -> execute.tcl | TCL gets -> TCL eval -> TCL puts | sender.py -> tx.sock -> PyTCL.recv()

if {[llength ${argv}] != 4} {
    error "ERROR: Exactly 4 arguments are required: <receiver.py> <rx.sock> <sender.py> <tx.sock>"
}

# Some characters for JSON string must be escaped with \ to properly serialize and deserialize string
# https://www.json.org/json-en.html
set TO_JSON_STRING {
    "\"" "\\\""
    "\\" "\\\\"
    "/"  "\\/"
    "\b" "\\b"
    "\f" "\\f"
    "\n" "\\n"
    "\r" "\\r"
    "\t" "\\t"
}

set forever 1

# Receiver channel from PyTCL to this TCL script:
# PyTCL.send() -> rx.sock -> receiver.py | execute.tcl
set rx_channel [open |[concat python3 [lindex ${argv} 0] [lindex ${argv} 1]] r]
fconfigure ${rx_channel} -blocking false -buffering line

# Sender channel from this TCL script back to PyTCL:
# execute.tcl | sender.py -> tx.sock -> PyTCL.recv()
set tx_channel [open |[concat python3 [lindex ${argv} 2] [lindex ${argv} 3]] w+]
fconfigure ${tx_channel} -blocking false -buffering line

# Directly executing TCL expression as-is received from PyTCL
# Sending result back to PyTCL in form of NDJSON: {"result":"<tcl-result>", "status": <tcl-status-code>}
# https://github.com/ndjson/ndjson-spec
proc execute {rx_channel tx_channel} {
    global TO_JSON_STRING

    # Get TCL expression from receiver.py
    set status [catch {gets ${rx_channel} line} length]

    # Evaluate received TCL expression and send result back to PyTCL using sender.py
    if {(${status} == 0) && (${length} >= 0)} {
        set status [catch {eval "${line}"} result]
        set result [string map ${TO_JSON_STRING} "${result}"]
        puts ${tx_channel} "{\"result\":\"${result}\",\"status\":${status}}"
    }

    # Close all opened channels and exit this TCL script
    if {[eof ${rx_channel}]} {
        close ${rx_channel}
        close ${tx_channel}
        set ::forever 0
    }
}

# It will call TCL procedure 'execute' for every new printed line from receiver.py standard output (stdout)
fileevent ${rx_channel} readable [list execute ${rx_channel} ${tx_channel}]
vwait forever
exit 0
