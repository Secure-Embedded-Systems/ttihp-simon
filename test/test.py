# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import RisingEdge

def hex_to_bits(hex_constant):
    binary_string = bin(int(hex_constant, 16))[2:]
    binary_string = binary_string.zfill(len(hex_constant) * 4)
    rev_binary_string = binary_string[::-1]
    for bit in rev_binary_string:
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


@cocotb.coroutine
async def store_result(dut, store_result_reg):
    while True:
        await RisingEdge(dut.clk)
        if dut.uo_out.value.is_resolvable and dut.uo_out.value.integer is not None:
            if (dut.uo_out.value.integer >> 7) & 1:
                store_result_reg.shift_right(dut.uo_out.value.integer & 1)
        
@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    store_result_reg = ShiftRegister128()

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    cocotb.start_soon(store_result(dut, store_result_reg))
    
    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    key_vectors = [ "d2427fba047e7fdc9fa45d04aa7a2ab7", 
                    "03dec884adc6ef3e1fa6bc445d5c5afe", 
                    "58c6c42c70324f5d60ee1efed7f0ffdf", 
                    "b25091ce2508d99a3d3a7f9c14223def", 
                    "7474eaa6713849fe2d48257aa6ee77fd", 
                    "359032b633587fbd65c2ee3c0494d7ba", 
                    "e6b41ff02e38fd7d2ea6e78ad3382ebc", 
                    "bc6a1fd877e2dffcdd2c015ef40afff3", 
                    "9ffa23b6b5266eff582e20ca6af647da", 
                    "7132fb36a99ee7fd8f0e5b42ccc4eb7f", 
                    "e0bae594243a7da7cb26a2605bc025fa", 
                    "2ac6813ed048ddb543a4a8307ae69bbf", 
                    "7a74c204f2fa672edc0043f69f8cf7cf", 
                    "3d8815c09d6afbde74d61f78698277ff", 
                    "30b45f725b2cece7b756f4c209c05fdf", 
                    "6c66f0f8e55077fec32c24729f8ee3de"]
    
    plain_vectors = [ "9f8e9892959afeeea080f1ea63e65b37", 
                      "d5be0328b8f87ffee3ecce3263f6ffc4", 
                      "49b261a460f273fce1209710987477d7", 
                      "4b28f378c35a5b9eac984d34c4de4d6a", 
                      "a6d89b14def82fffd738ce142088b8fd", 
                      "f52491fa7f6c7dd7e4da903cc15a6f1f", 
                      "5f3ab93e6b9c7f9e4754d24eaf2479ee", 
                      "02be0e8e26969ffde6042454e75473ee", 
                      "9bf44dc02af8e7d7b9ceb3ba1950fbec", 
                      "9e6646d808e04f3e85b241aa6334ebbb", 
                      "6410f08a4e4c5fef33c42bfed71cfffe", 
                      "9afcbf48a204f5f2dec2709c10ee55e2", 
                      "997c48caf9047fc9101a1368a4a0fe6f", 
                      "c0c0bc124e5ee5973a64cea8ad0073ff", 
                      "960e35fac5ac74fdf87e75ec42fe4ddf", 
                      "ba5e7a389ff2ef731906f3762570becd"]
    
    cipher_vectors = [ "a6b6277142e0661ccd32dc221c74caf0",
                       "8687e7c1beb3b9753befec46ca36b925",
                       "eb1f5c3a9a583ec336fa9e136eb8e899",
                       "0eb440e457fd1392f85d4b3546e99f35",
                       "2dc731cceaeef69860a1c69b79f36675",
                       "d098a10553f42e796c1f5af6f82acd10",
                       "e432578762ddac708c0f42fa65dcf44c",
                       "bcc1c5cf842bb24b461db48ecf307e88",
                       "da30502f545df510ae078ee70229fd59",
                       "1ca811e19a250aae77c828bdbf235d9e",
                       "4a3d385fd1d6d4d51a79f3aa80f71a41",
                       "7585fad2b65b6899ff7d5f4dcd847b14",
                       "32a8cf4c82a798ad27f8c4fb69fd5c64",
                       "a589e252e02c6e42904ba985307593f3",
                       "038ccd765f330e563046e2386a02f8e5",
                       "818a1b1154be81c393fc0371e6511ef8"]
    # clear registers
    # data_rdy = 3, debug_port=0, data_in=0 for 130 cycles
    dut.ui_in.value = ((3 << 6) + (0 << 5) + 0)
    await ClockCycles(dut.clk, 130)
    
    # data_rdy = 3, debug_port=1, data_in=0 for 130 cycles
    dut.ui_in.value = ((3 << 6) + (1 << 5) + 0)
    await ClockCycles(dut.clk, 130)

    # data_rdy = 3, debug_port=1, data_in=0
    dut.ui_in.value = ((3 << 6) + (0 << 5) + 0)
    
    dut._log.info("Test project behavior")

    for (key, pt, ct) in zip(key_vectors, plain_vectors, cipher_vectors):
        await ClockCycles(dut.clk, 2)
    
        # data_rdy = 0, debug_port =0, data_in = 0 for 2 cycles
        dut.ui_in.value = ((0 << 6) + (0 << 5) + 0)
        await ClockCycles(dut.clk, 2)
        
        # load pt
        for bit in hex_to_bits(pt):
            # data_rdy = 1, debug_port = 0, data_in = bit
            dut.ui_in.value = ((1 << 6) + (0 << 5) + bit)
            await ClockCycles(dut.clk, 1)
        
        # load key
        for bit in hex_to_bits(key):
            # data_rdy = 2, debug_port = 0, data_in = bit
            dut.ui_in.value = ((2 << 6) + (0 << 5) + bit)
            await ClockCycles(dut.clk, 1)

        # data_rdy = 0, debug_port = 0, data_in = 0
        dut.ui_in.value = ((0 << 6) + (0 << 5) + 0)
        await ClockCycles(dut.clk, 1)

        # start encryption
        # data_rdy = 3, debug_port = 0, data_in = 0
        dut.ui_in.value = ((3 << 6) + (0 << 5) + 0)
        await ClockCycles(dut.clk, 64*71)

        print(hex(store_result_reg.get_value()))
        assert(store_result_reg.get_value() == int(ct, 16))

        await ClockCycles(dut.clk, 2)

    
