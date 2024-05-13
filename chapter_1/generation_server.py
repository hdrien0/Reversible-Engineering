#Author : _hdrien
#404CTF 2024

import socket
import os
import zipfile
import io
import concurrent.futures
from sqlalchemy import create_engine
from crackme import generate_binary
from db import Database

PORT = int(os.getenv('GENERATION_SERVER_PORT', '9998'))
TOKEN_VALIDITY_DURATION = os.getenv('TOKEN_VALIDITY_DURATION', 20)
TOKEN_DELETED_AFTER = os.getenv('TOKEN_DELETED_AFTER', 120)

# Create SQLite database
engine = create_engine('sqlite:///tokens.db', echo=True)


def generate_zip_file(token, binary):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('crackme.bin', binary)
        zip_file.writestr('token.txt', token)
    return zip_buffer.getvalue()


def handle_generation(client_socket):
    try:
        db_session = Database(engine, TOKEN_VALIDITY_DURATION, TOKEN_DELETED_AFTER)
        db_session.clean_sessions()
        token = os.urandom(16).hex()
        binary, solution = generate_binary(token,15)
        # Store token and strings in the database
        success = db_session.create_session(token, solution)
        if not success:
            client_socket.sendall(b"Cette erreur a une chance infime de se produire... Jouez au loto !\n")
            return

        # Create a zip file and send it to the client
        zip_data = generate_zip_file(token, binary)
        client_socket.sendall(zip_data)
        client_socket.close()
    except Exception as e:
        client_socket.sendall(b"Une erreur est survenue.. Fermeture de la connection :(\n")

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
