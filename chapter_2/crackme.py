#Author : _hdrien
#404CTF 2024

import r2pipe
import os
import random

from generation_utils import patch_and_compile, transform_bytes, transform_string, generate_random_circuit, random_alphanumeric_string, get_function_instructions
from logic import *

def generate_assembly_instructions(circuit, token, operation_number):
    patches = [
        ("//INSTRUCTIONS", circuit.to_c_code("c", 2))
    ]
    binary_path = patch_and_compile("operation.c", patches, f"{token}_{operation_number}.c", True, False)
    r2 = r2pipe.open(binary_path, flags=['-2'])
    instructions = get_function_instructions(r2, "sym.operation", f"operation_{token}_{operation_number}")
    os.remove(binary_path)
    return instructions

def generate_main_binary(token, circuit, host, port):
    patches = [
        ("//HOST", f'host = "{host}";'),
        ("//PORT", f'port = {port};'),
        ("//TOKEN", f'token = "{token}\\n";'),
        ("//INSTRUCTIONS", circuit.to_c_code("c", 2)),
    ]
    binary = patch_and_compile("main.c", patches, f"{token}.c")
    return binary

def generate_solutions_and_circuits(nb_verifications, nb_circuits_min, nb_gates_min):

    solution = ""
    start_buffer_value = []

    server_circuits = []
    binary_circuit = generate_random_circuit([NGATE, CGATE, TGATE], 8, random.randint(nb_gates_min, nb_gates_min*2))
    for _ in range(random.randint(nb_circuits_min, nb_circuits_min+1)):
        circuit = generate_random_circuit([NGATE, CGATE, TGATE], 8, random.randint(nb_gates_min, nb_gates_min*2))
        server_circuits.append(circuit)

    for _ in range(nb_verifications):
        verif_solution = random_alphanumeric_string(16)
        output = transform_string(server_circuits[0], verif_solution)
        for circuit in server_circuits[1:]:
            output = transform_bytes(circuit, output)
        verif_start_buffer_value = transform_bytes(binary_circuit.inverse(), output)
        solution += verif_solution
        start_buffer_value += verif_start_buffer_value

    return solution, bytes(start_buffer_value), server_circuits, binary_circuit