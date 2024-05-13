#Author : _hdrien
#404CTF 2024

from logic import *
from itertools import product, permutations
import socket
import dill

ADDRESS = "challenges.404ctf.fr"
PORT = 32274

def is_circuit_duplicate(gates,bits,existing_circuits):
    circuit = Circuit(gates, bits)
    for circuits in existing_circuits.values():
        if circuit in circuits:
            return None
    return circuit

def generate_optimal_circuits(gate_library, bits, max_size): #gate_library is a list of available gate classes, bits is the number of bits in the circuit, max_size is the maximum number of gates in the circuit

    optimal_circuits = {}
    optimal_circuits[0] = [Circuit([], bits)]

    # Each of the generated circuits is the optimal way to perform a unique bijection between {0,1}^bits and {0,1}^bits
    # Dynamic programming to generate optimal circuits of increasing size. Based on the paper "Synthesis of Reversible Logic Circuits"
    for size in range(1, max_size + 1):

        candidates = []

        for circuit, gate in product(optimal_circuits[size - 1], gate_library):
            for mask in permutations(range(bits), gate.arity):
                gates = circuit.gates + [gate(mask)]
                candidates.append((gates, bits, optimal_circuits))

        print(f"\nTesting a total of {len(candidates)} circuits of size {size}")

        optimal_circuits[size] = []

        results = [is_circuit_duplicate(*i) for i in candidates]
        #results = multiprocessing.Pool().starmap(is_circuit_duplicate, args)
        for circuit in results:
            if (circuit!=None and circuit not in optimal_circuits[size]):
                optimal_circuits[size].append(circuit)
        
        print(f"{len(optimal_circuits[size])} optimal circuits of size {size} were found!")

    return optimal_circuits

optimal_circuits = dill.load(open("3bit_optimal_circuits.p", "rb")) # Load the precomputed optimal circuits

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ADDRESS, PORT))
client_socket.recv(1024)
client_socket.recv(1024)

for _ in range(4):
    a = client_socket.recv(1024).decode("utf-8").strip()
    circuit = circuit_from_json(a)
    print(f"Received circuit {circuit}")
    solution = circuit

    for size in range(min(len(optimal_circuits), len(circuit.gates))):
        for optimal_circuit in optimal_circuits[size]:
            if circuit == optimal_circuit:
                solution = optimal_circuit



    print(f"Sending solution {solution.to_json()}\n")
    client_socket.sendall((solution.to_json() + "\n").encode("utf-8"))
    print(client_socket.recv(1024).decode("utf-8").strip())

