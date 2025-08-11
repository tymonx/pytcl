#!/usr/bin/env tclsh
# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

# Execution flow:
# PyTCL.send()/recv() <-> <connection> <-> execute.py <-> execute.tcl | TCL gets/puts <-> TCL eval

if {[llength ${argv}] < 1} {
    error "ERROR: Exactly 1 argument is required: <address>"
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

# Detect if current environment has python3 (recommended) or python (potentially python2?)
if {[auto_execok python3] ne ""} {
    set python "python3"
} else {
    set python "python"
}

set script [file join [file dirname [file normalize [info script]]] "execute.py"]

# Transmitter channel between PyTCL and this TCL script:
set channel [open |[list "${python}" "${script}" [lindex ${argv} 0]] RDWR]
fconfigure ${channel} -blocking false -buffering line

# Directly executing TCL expression as-is received from PyTCL
# Sending result back to PyTCL in form of NDJSON: {"result":"<tcl-result>", "status": <tcl-status-code>}
# https://github.com/ndjson/ndjson-spec
proc execute {channel} {
    global TO_JSON_STRING

    while {1} {
        # Get TCL expression from execute.py
        set status [catch {gets ${channel} line} length]

        # Evaluate received TCL expression and send result back to PyTCL using execute.py
        if {(${status} == 0) && (${length} >= 0)} {
            set status [catch {eval "${line}"} result]
            set result [string map ${TO_JSON_STRING} "${result}"]
            puts ${channel} "{\"result\":\"${result}\",\"status\":${status}}"
        }

        # Close all opened channels and exit this TCL script
        if {[eof ${channel}]} {
            close ${channel}
            set ::forever 0
            break
        }
    }
}

# It will call TCL procedure 'execute' for every new printed line from execute.py standard output (stdout)
fileevent ${channel} readable [list execute ${channel}]
vwait forever
exit 0
