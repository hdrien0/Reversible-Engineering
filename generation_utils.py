import os
import random
import string
from logic import Circuit

def patch_and_compile(filename,patches,temp_filename, return_file=False, strip_symbols=True):
    # Apply patches to the code
    TEMPLATE = None
    with open(filename, "r") as file:
        TEMPLATE = file.read()

    for patch in patches:
        TEMPLATE = TEMPLATE.replace(patch[0], patch[1])
    
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    with open(f"tmp/{temp_filename}", "w") as file:
        file.write(TEMPLATE)
    
    # Compile the file
    os.system(f"gcc tmp/{temp_filename} {'-s' if strip_symbols else ''} -o tmp/{temp_filename.replace('.c','.bin')}")
    binary = open(f"tmp/{temp_filename.replace('.c','.bin')}", "rb").read()
    os.remove(f"tmp/{temp_filename}")
    if return_file:
        return f"tmp/{temp_filename.replace('.c','.bin')}"
    os.remove(f"tmp/{temp_filename.replace('.c','.bin')}")
    return binary

def generate_random_circuit(gate_library, bits, size):
    gates = []
    for _ in range(size):
        gate = random.choice(gate_library)
        mask = random.sample(range(bits), gate.arity)
        gates.append(gate(mask))
    return Circuit(gates, bits)

def transform_bytes(circuit, input):
    output = []
    for i in input:
        bits = tuple(int(bit) for bit in bin(i)[2:].zfill(8)[::-1])
        result = circuit.output(bits)
        output += bytes((sum(bit << i for i, bit in enumerate(result)),))
    return output

def transform_string(circuit, string):
    return transform_bytes(circuit, [ord(char) for char in string])

def random_alphanumeric_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

### FOR CHAPTER 3 ###

def get_function_address(r2, function_name):
    r2.cmd(f"aaa")
    return r2.cmdj(f"afij {function_name}")[0]["offset"]

def get_function_length(r2, function_address):
    r2.cmd(f"af @ {hex(function_address)}")
    return r2.cmdj(f"afij @ {function_address}")[0]["size"]

def get_function_instructions(r2, function_name, temp_filename):

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    function_address = get_function_address(r2, function_name)
    r2.cmd(f"wtf tmp/{temp_filename} {get_function_length(r2, function_address)} @ {hex(function_address)}")
    instructions = None
    with open(f"tmp/{temp_filename}", "rb") as file:
        instructions = file.read()
    os.remove(f"tmp/{temp_filename}")
    return instructions

