// SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
// SPDX-License-Identifier: Apache-2.0

// Simple DUT (Design Under Test) module.
module dut(
    input i_clk,
    input i_rst,
    input i_valid,
    input i_data,
    output logic o_data
);
    always_ff @(posedge i_clk) begin: main
        if (i_rst) begin
            o_data <= '0;
        end else if (i_valid) begin
            o_data <= i_data;
        end
    end
endmodule
