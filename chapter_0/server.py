#Author : _hdrien
#404CTF 2024

import dill
from logic import *
from generation_utils import generate_random_circuit
import os

CIRCUITS_FILE = "3bit_optimal_circuits.p"
OPTIMAL_CIRCUITS = None
FLAG = os.getenv('FLAG', '404CTF{fake_flag}')
MESSAGES = [
    "Voici un circuit réversible aléatoire sur 3 bits. Donnez un circuit équivalent optimal dans le même format. Les bits de contrôle seront notés en premier.\n",
    "Encore un !\n",
    "Un autre !\n",
    "Un dernier !\n",
]

def main():
    try:
        for i in range(len(MESSAGES)):
            print(MESSAGES[i])
            circuit = generate_random_circuit([NGATE, CGATE, TGATE], 3, 8)
            print(circuit.to_json())
            answer_json = input().strip()
            answer = circuit_from_json(answer_json)
            correct_answer = find_optimal_circuit(circuit)
            if not ((answer == correct_answer) and (len(answer.gates) == len(correct_answer.gates))):
                print("Ce n'est pas la bonne réponse :(")
                return
        
        print(f"Bravo ! Voici le flag : {FLAG}")
            
    except Exception as e:
        print("Une erreur est survenue.. Fermeture de la connection :(")

def find_optimal_circuit(circuit):
    for size in range(min(len(OPTIMAL_CIRCUITS), len(circuit.gates))):
        for optimal_circuit in OPTIMAL_CIRCUITS[size]:
            if circuit == optimal_circuit:
                return optimal_circuit
    return circuit


if __name__ == "__main__":
    print("Chargement...")
    OPTIMAL_CIRCUITS = dill.load(open(CIRCUITS_FILE, "rb"))
    main()