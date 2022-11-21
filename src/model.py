import math

DENORMAL = False

def to_binary(x):
    return list(reversed([int(c == '1') for c in f"{x:08b}"]))

# Slightly modified IEEE 754:
#   exp=max is used for more normals (instead of inf/nan)
#   -0 is replaced with NaN
def to_float(x, SIGN=1, EXP=4, EXPBIAS=7, MANT=3):
    assert SIGN in [0, 1], SIGN
    assert type(EXP) == int and EXP >= 0, EXP
    assert type(EXPBIAS) == int, EXPBIAS
    assert type(MANT) == int and MANT >= 0, MANT
    assert type(x) == int and x >= 0 and x < 2**(EXP+MANT+1), x

    sign = (x >> (EXP+MANT)) & SIGN
    exp =  (x >> MANT)       & (2**EXP - 1)
    mant = (x)               & (2**MANT - 1)

    if exp > 0:
        # Normal
        return (-1.0)**sign * 2 ** (exp - EXPBIAS) * (1 + mant / 2**MANT)
    else:
        # Denormal/Zero/NaN
        if mant == 0 and sign == 1:
            return math.nan
        # Denormal (or return 0 if don't want to support)
        if DENORMAL:
            return (-1.0)**sign * 2 ** (1 - EXPBIAS) * (0 + mant / 2**MANT)
        else:
            return 0

# All the testcases from half precision wikipedia page
assert to_float(0b0_00000_0000000000, EXP=5, EXPBIAS=15, MANT=10) == 0.0
if DENORMAL:
    assert round(to_float(0b0_00000_0000000001, EXP=5, EXPBIAS=15, MANT=10),15) == 0.000000059604645
    assert round(to_float(0b0_00000_1111111111, EXP=5, EXPBIAS=15, MANT=10),12) == 0.000060975552
else:
    assert round(to_float(0b0_00000_0000000001, EXP=5, EXPBIAS=15, MANT=10),15) == 0.0
    assert round(to_float(0b0_00000_1111111111, EXP=5, EXPBIAS=15, MANT=10),12) == 0.0
assert round(to_float(0b0_00001_0000000000, EXP=5, EXPBIAS=15, MANT=10),14) == 0.00006103515625
assert round(to_float(0b0_01101_0101010101, EXP=5, EXPBIAS=15, MANT=10),8) == 0.33325195
assert round(to_float(0b0_01110_1111111111, EXP=5, EXPBIAS=15, MANT=10),8) == 0.99951172
assert to_float(0b0_01111_0000000000, EXP=5, EXPBIAS=15, MANT=10) == 1.0
assert round(to_float(0b0_01111_0000000001, EXP=5, EXPBIAS=15, MANT=10),8) == 1.00097656
assert to_float(0b0_11110_1111111111, EXP=5, EXPBIAS=15, MANT=10) == 65504
assert to_float(0b0_11111_0000000000, EXP=5, EXPBIAS=15, MANT=10) == 65536  # Normally infinity
assert math.isnan(to_float(0b1_00000_0000000000, EXP=5, EXPBIAS=15, MANT=10))  # Normally -0
assert to_float(0b1_10000_0000000000, EXP=5, EXPBIAS=15, MANT=10) == -2
assert to_float(0b1_11111_0000000000, EXP=5, EXPBIAS=15, MANT=10) == -65536  # Normally -infinity
# Also test the "supernormal" numbers
assert to_float(0b0_11111_1111111111, EXP=5, EXPBIAS=15, MANT=10) == 131008



all_fp8 = [to_float(i) for i in range(256)]

def closest_fp8(f):
    distances = [abs(all_fp8[i] - f) for i in range(len(all_fp8))]
    min_distance = min(distances)
    minimums = [i for i in range(len(all_fp8)) if distances[i] == min_distance]
    # If flushing denormal to 0, lots of representations for 0 - use canonical one.
    if not DENORMAL:
        minimums = [m for m in minimums if to_float(m) != 0.0 or m == 0b0_0000_000]
    if len(minimums) == 1:
        return minimums[0]
    elif len(minimums) == 2:
        # Round to nearest even
        if minimums[0] % 2 == 0:
            return minimums[0]
        elif minimums[1] % 2 == 0:
            return minimums[1]
    elif math.isnan(f):
        return 0b1_0000_000
    raise ValueError(f"Don't know what to do with input {f} with {len(minimums)=}")

def get_8bit_op(fp_op):
    def op_8bit(a, b):
        # print(f"{a:08b} + {b:08b}")
        # assert closest_fp8(to_float(a)) == a
        # assert closest_fp8(to_float(b)) == b

        a = to_float(a)
        b = to_float(b)
        # assert to_float(closest_fp8(a)) == a or math.isnan(a) and math.isnan(to_float(closest_fp8(a)))
        # assert to_float(closest_fp8(b)) == b or math.isnan(b) and math.isnan(to_float(closest_fp8(b)))
        c = fp_op(a, b)

        # print(f"fp_op({a}, {b}) = {c} ~= {to_float(closest_fp8(c))}")
        c = closest_fp8(c)
        # print(f"{c:08b}")
        return c
    return op_8bit



# def generate_truthtable(fp_op):
#     def op_8bit(a, b):
#         # print(f"{a:08b} + {b:08b}")
#         # assert closest_fp8(to_float(a)) == a
#         # assert closest_fp8(to_float(b)) == b

#         a = to_float(a)
#         b = to_float(b)
#         # assert to_float(closest_fp8(a)) == a or math.isnan(a) and math.isnan(to_float(closest_fp8(a)))
#         # assert to_float(closest_fp8(b)) == b or math.isnan(b) and math.isnan(to_float(closest_fp8(b)))
#         c = fp_op(a, b)

#         # print(f"fp_op({a}, {b}) = {c} ~= {to_float(closest_fp8(c))}")
#         c = closest_fp8(c)
#         # print(f"{c:08b}")
#         return c

#     truthtable_inputs = []
#     truthtable_outputs = []
#     for i in range(len(all_fp8)):
#         for j in range(len(all_fp8)):
#             truthtable_inputs.append(to_binary(i) + to_binary(j))
#             truthtable_outputs.append(to_binary(op_8bit(i, j)))
#     return truthtable_inputs, truthtable_outputs

# def mul_circuit_implementation(input):
#     input1 = input[:8]
#     input2 = input[8:]
#     output = [False] * 8

#     # Sign bit 7
#     output[7] = input1[7] ^ input2[7]

#     # Exponent bits 3:6
#     output[3] = input1[3] ^ input2[3]
#     carry = input1[3] & input2[3]
#     output[4] = input1[4] ^ input2[4] ^ carry
#     carry = (carry and input1[4]) or (input1[4] and input2[4]) or (input2[4] and carry)
#     output[5] = input1[5] ^ input2[5] ^ carry
#     carry = (carry and input1[5]) or (input1[5] and input2[5]) or (input2[5] and carry)
#     output[6] = input1[6] ^ input2[6] ^ carry
#     carry = (carry and input1[6]) or (input1[6] and input2[6]) or (input2[6] and carry)
#     if carry:
#         output[0] = output[1] = output[2] = output[3] = output[4] = output[5] = output[6] = True

#     # Mantissa bits 0:2, plus the implicit 1/0 bit in front
#     for i, x in enumerate([input1[0], input1[1], input1[2], any(output[3:6])]):
#         output[0]
#         pass

#     return output

# for input, output in zip(*generate_truthtable(lambda a, b: a * b)):
#     assert mul_circuit_implementation(input) == output, f"{input} yields {mul_circuit_implementation(input)} but expected {output}"
# print("Verified!")

# def add_circuit_implementation(input):
#     # No idea how, this sounds hard
#     pass

# for input, output in zip(*generate_truthtable(lambda a, b: a * b)):
#     assert add_circuit_implementation(input) == output