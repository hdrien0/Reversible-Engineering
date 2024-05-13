import dill
from logic import *

CIRCUITS_FILE = "3bit_optimal_circuits_serialized.p"
circuits_dict = dill.load(open(CIRCUITS_FILE, "rb"))

# for size in circuits_dict:
#     print(f"{len(circuits_dict[size])} optimal circuits of size {size} were found!")

cleaned_circuits_dict = {}

for size in circuits_dict:
    print(f"{len(circuits_dict[size])} optimal circuits of size {size} were found!")
    cleaned_circuits_dict[size] = []
    for circuit in circuits_dict[size]:
        gates = []
        for gate in circuit:
            if gate[0] == "NOT":
                gates.append(NGATE(gate[1]))
            elif gate[0] == "CNOT":
                gates.append(CGATE(gate[1]))
            elif gate[0] == "TOFFOLI":
                gates.append(TGATE(gate[1]))
        
        cleaned_circuits_dict[size].append(Circuit(gates, 3))
        #cleaned_circuits_dict[size].append(Circuit(circuit.gates, 3))
    
dill.dump(cleaned_circuits_dict, open("3bit_optimal_circuits.p", "wb"))