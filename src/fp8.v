module cchan_fp8_multiplier (
  input [7:0] io_in,
  output [7:0] io_out
);
    wire clk = io_in[0];
    wire [2:0] ctrl = io_in[3:1];
    wire [3:0] data = io_in[7:4];
    // wire [6:0] led_out;
    // assign io_out[6:0] = led_out;
    // wire [5:0] seed_input = io_in[7:2];

    reg [8:0] operand1;
    reg [8:0] operand2;
    // For now we're commenting this out and leaving the results unbuffered.
    // reg [8:0] result_out;
    // assign io_out = result_out;

    always @(posedge clk) begin
        if (!ctrl[0]) begin  // if first CTRL bit is off, we're in STORE mode
            if (!ctrl[1]) begin  // second CTRL bit controls whether it's the first or second operand
                if (!ctrl[2]) begin  // third CTRL bit controls whether it's the upper or lower half
                    operand1[3:0] <= data;
                end else begin
                    operand1[7:4] <= data;
                end
            end else begin
                if (!ctrl[2]) begin
                    operand2[3:0] <= data;
                end else begin
                    operand2[7:4] <= data;
                end
            end
        end else begin  // if first CTRL bit is on, this is reserved.
            // TODO
            // if (!ctrl[1] && !ctrl[2]) begin
            //     result_out[7:0] <= 0;
            // end
        end
    end

    // Compute result_out in terms of operand1, operand2
    fp8mul mul1(
        .sign1(operand1[7]),
        .exp1(operand1[6:3]),
        .mant1(operand1[2:0]),
        .sign2(operand2[7]),
        .exp2(operand2[6:3]),
        .mant2(operand2[2:0]),
        .sign_out(io_out[7]),
        .exp_out(io_out[6:3]),
        .mant_out(io_out[2:0])
    );
endmodule

module fp8mul (
  input sign1,
  input [3:0] exp1,
  input [2:0] mant1,

  input sign2,
  input [3:0] exp2,
  input [2:0] mant2,

  output sign_out,
  output [3:0] exp_out,
  output [2:0] mant_out
);
    assign sign_out = sign1 ^ sign2;
    assign exp_out = (exp1 == 0 || exp2 == 0) ? 0 : (exp1 + exp2 - 7);  // Exponent bias is 7

    wire [7:0] full_mant = ({1'b1, mant1} * {1'b1, mant2});
    assign mant_out = full_mant[6:4];
endmodule
