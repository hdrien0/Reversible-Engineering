#Author : _hdrien
#404CTF 2024

import random
from logic import *
from generation_utils import patch_and_compile, transform_string, generate_random_circuit, random_alphanumeric_string

def generate_binary(token,nb_gates_min):
    nb_gates = random.randint(nb_gates_min, nb_gates_min*2)
    secret = random_alphanumeric_string(16)
    circuit = generate_random_circuit([NGATE, CGATE, TGATE], 8, nb_gates)
    output_string  = ''.join('\\x{:02x}'.format(c) for c in transform_string(circuit, secret))
    patches = [
        ("//SECRET", f'memcpy(buf, "{output_string}", 16);'),
        ("//INSTRUCTIONS", circuit.to_c_code("c", 2))
    ]
    binary = patch_and_compile("main.c", patches, f"{token}.c")
    return binary, secret