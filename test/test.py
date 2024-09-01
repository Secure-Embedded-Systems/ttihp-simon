# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import RisingEdge
from cocotb.triggers import BinaryValue

def hex_to_bits(hex_constant):
    binary_string = bin(int(hex_constant, 16))[2:]
    binary_string = binary_string.zfill(len(hex_constant) * 4)
    for bit in binary_string:
        yield int(bit)


class ShiftRegister128:
    def __init__(self):
        self.register = [0] * 128

    def shift_left(self, new_bit=0):
        if new_bit not in [0, 1]:
            raise ValueError("new_bit must be 0 or 1")
        self.register = self.register[1:] + [new_bit]

    def shift_right(self, new_bit=0):
        if new_bit not in [0, 1]:
            raise ValueError("new_bit must be 0 or 1")
        self.register = [new_bit] + self.register[:-1]

    def get_value(self):
        return int("".join(map(str, self.register)), 2)

    def __str__(self):
        return "".join(map(str, self.register))

store_result_reg = ShiftRegister128()

@cocotb.coroutine
async def store_result(dut):
    while True:
        await RisingEdge(dut.clk)
        uo_out_value = BinaryValue(dut.uo_out.value)
        if uo_out_value.is_resolvable and uo_out_value.integer is not None:            
            # check if valid bit is asserted and store data output if so
            if ((dut.uo_out.value.integer >> 7) & 1):
                store_result_reg.shift_right(dut.uo_out.value & 1)
        
@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    cocotb.start_soon(store_result(dut))
    
    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1


    # clear registers
    # data_rdy = 3, debug_port=0, data_in=0 for 130 cycles
    dut.ui_in.value = ((3 << 6) + (0 << 5) + 0)
    await ClockCycles(dut.clk, 130)
    
    # data_rdy = 3, debug_port=1, data_in=0 for 130 cycles
    dut.ui_in.value = ((3 << 6) + (1 << 5) + 0)
    await ClockCycles(dut.clk, 130)

    # data_rdy = 0, debug_port =0, data_in = 0 for 2 cycles
    dut.ui_in.value = ((0 << 6) + (0 << 5) + 0)
    await ClockCycles(dut.clk, 2)
    
    key_vectors = [ "0xd2427fba047e7fdc9fa45d04aa7a2ab7",
                    "0x03dec884adc6ef3e1fa6bc445d5c5afe",
                    "0x58c6c42c70324f5d60ee1efed7f0ffdf",
                    "0xb25091ce2508d99a3d3a7f9c14223def" ]
    
    plain_vectors = [ "0x9f8e9892959afeeea080f1ea63e65b37",
                      "0xd5be0328b8f87ffee3ecce3263f6ffc4",
                      "0x49b261a460f273fce1209710987477d7",
                      "0x4b28f378c35a5b9eac984d34c4de4d6a" ]
    
    cipher_vectors = [ "0xa6b6277142e0661ccd32dc221c74caf0",
                       "0x8687e7c1beb3b9753befec46ca36b925",
                       "0xeb1f5c3a9a583ec336fa9e136eb8e899",
                       "0x0eb440e457fd1392f85d4b3546e99f35" ]
    
    dut._log.info("Test project behavior")

    for (key, pt, ct) in zip(key_vectors, plain_vectors, cipher_vectors):
        
        # load pt
        for bit in hex_to_bits(pt):
            # data_rdy = 1, debug_port = 0, data_in = bit
            dut.ui_in.value = ((1 << 6) + (0 << 5) + bit)
            await ClockCycles(dut.clk, 1)
        
        # load key
        for bit in hex_to_bits(key):
            # data_rdy = 2, debug_port = 0, data_in = bit
            dut.ui_in.value = ((1 << 6) + (0 << 5) + bit)
            await ClockCycles(dut.clk, 1)


        # data_rdy = 0, debug_port = 0, data_in = 0
        dut.ui_in.value = ((0 << 6) + (0 << 5) + 0)
        await ClockCycles(dut.clk, 1)

        # start encryption
        # data_rdy = 3, debug_port = 0, data_in = 0
        dut.ui_in.value = ((3 << 6) + (0 << 5) + 0)
        await ClockCycles(dut.clk, 64*71)
        
        assert(store_result_reg.get_value() == int(ct, 16))
        
    
