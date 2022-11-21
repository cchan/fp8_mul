import cocotb
from cocotb.triggers import Timer
from model import get_8bit_op, to_binary, to_float


@cocotb.test()
async def test_all_inputs(dut):
    """Test all possible pairs of 8-bit inputs."""

    async def store(operand, half, data):
        dut.io_in[0].value = 0
        dut.io_in[1].value = 0
        dut.io_in[2].value = operand
        dut.io_in[3].value = half
        for i in range(4):
            dut.io_in[4+i].value = data[i]
        await Timer(1, units="ms")
        dut.io_in[0].value = 1
        await Timer(1, units="ms")

    fp8_mul_model = get_8bit_op(lambda a, b: a * b)

    # TODO: Test in random order
    for i in [0b01010101]:
        for j in [0b10101010]:
            in1 = to_binary(i)
            in2 = to_binary(j)
            await store(0, 0, in1[:4])
            await store(0, 1, in1[4:])
            await store(1, 0, in2[:4])
            await store(1, 1, in2[4:])
            correct = fp8_mul_model(i, j)
            assert dut.io_out.value.binstr == f"{correct:08b}", f"{to_float(i)} ({i:08b}) * {to_float(j)} ({j:08b}) = {to_float(dut.io_out.value.integer)} ({dut.io_out.value.integer:08b}), should be {to_float(correct)} ({correct:08b})"
