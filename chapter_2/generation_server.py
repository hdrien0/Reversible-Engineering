#Author : _hdrien
#404CTF 2024

import socket
import os
import zipfile
import io
import concurrent.futures
from sqlalchemy import create_engine
from crackme import generate_solutions_and_circuits, generate_assembly_instructions, generate_main_binary
from db import Database

PORT = int(os.getenv('GENERATION_SERVER_PORT', '9990'))
SERVER_HOSTNAME = os.getenv('SERVER_HOSTNAME', '127.0.0.1')
INSTRUCTIONS_SERVER_OUTSIDE_PORT = os.getenv('INSTRUCTIONS_SERVER_OUTSIDE_PORT', 9992)
TOKEN_VALIDITY_DURATION = os.getenv('TOKEN_VALIDITY_DURATION', 600)
TOKEN_DELETED_AFTER = os.getenv('TOKEN_DELETED_AFTER', 900)

# Create SQLite database
engine = create_engine('sqlite:///tokens.db', echo=False)

def generate_zip_file(token, binary):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('crackme.bin', binary)
        zip_file.writestr('token.txt', token)
    return zip_buffer.getvalue()


def handle_generation(client_socket):
    try :
        db_session = Database(engine, TOKEN_VALIDITY_DURATION, TOKEN_DELETED_AFTER)
        db_session.clean_sessions()
        token = os.urandom(16).hex()
        solution, start_buffer_values, server_circuits, binary_circuit = generate_solutions_and_circuits(3, 2, 15)
        
        print(f"Token: {token}")
        print(f"Number of server circuits: {len(server_circuits)}")

        for i in range (len(solution)//16):
            print(f"Solution part {i}: {solution[i*16:(i+1)*16]}")

        success = db_session.create_session(token, solution, start_buffer_values)
        if not success:
            client_socket.sendall(b"Cette erreur a une chance infime de se produire... Joue au loto !\n")
            return

        for i, circuit in enumerate(server_circuits):
            instructions = generate_assembly_instructions(circuit, token, i)
            db_session.add_operation(token, instructions, i)

        binary = generate_main_binary(token, binary_circuit, SERVER_HOSTNAME, INSTRUCTIONS_SERVER_OUTSIDE_PORT)

        # Create a zip file and send it to the client
        zip_data = generate_zip_file(token, binary)
        client_socket.sendall(zip_data)
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")
        client_socket.sendall(b"Une erreur est survenue... Fermeture de la connection :(\n")
        client_socket.close()


def main():
    generation_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    generation_socket.bind(('0.0.0.0', PORT))
    generation_socket.listen(5)
    print(f"Generation server listening on port {PORT}...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            client_socket, addr = generation_socket.accept()
            executor.submit(handle_generation, client_socket)

if __name__ == "__main__":
    main()
