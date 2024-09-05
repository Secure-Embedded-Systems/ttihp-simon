//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    19:14:37 11/13/2013 
// Design Name: 
// Module Name:    top_module 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module simon_module(clk,reset,data_in,data_rdy,cipher_out,valid,debug_port);
   
   input clk,data_in,reset;
   input [1:0] data_rdy;
   input 	   debug_port;
   output reg  cipher_out;
   output 	   valid;
   
   wire 	   key;
   wire 	   cipher_data;
   wire [5:0]  bit_counter;
   wire [6:0]  round_counter;

   simon_datapath_shiftreg datapath(.clk(clk), 
									.reset(reset),
									.data_in(data_in), 
									.data_rdy(data_rdy), 
									.key_in(key), 
									.cipher_out(cipher_data), 
									.round_counter(round_counter), 
									.bit_counter(bit_counter),
									.valid(valid));
   
   // FIXED KEY IMPLEMENTATION TO KEY VALUE 00000000_00000000_00000000_00000000
   // THIS DESIGN FORCES ALL KEY BITS TO 0 UPON LOADING

   simon_key_expansion_shiftreg key_exp(.clk(clk), 
										.reset(reset), 
										.data_in(1'b0),   // was: data_in 
										.data_rdy(data_rdy), 
										.key_out(key), 
										.bit_counter(bit_counter), 
										.round_counter(round_counter));
   
   always@(*)
	 begin
		if(debug_port==1)
		  cipher_out = key;
		else 
		  cipher_out = cipher_data;
	 end
   

endmodule
