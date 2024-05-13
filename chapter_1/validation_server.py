#Author : _hdrien
#404CTF 2024

import os
from sqlalchemy import create_engine
from db import Database

FLAG = os.getenv('FLAG', '404CTF{fake_flag}')
TOKEN_VALIDITY_DURATION = os.getenv('TOKEN_VALIDITY_DURATION', 20)
TOKEN_DELETED_AFTER = os.getenv('TOKEN_DELETED_AFTER', 120)

# Create SQLite database
engine = create_engine('sqlite:///tokens.db')

def main():

    try:
        db_session = Database(engine, TOKEN_VALIDITY_DURATION, TOKEN_DELETED_AFTER)
        print("Token ? ")
        token = input().strip()
        session = db_session.get_session(token)
        if not session:
            print("Token invalide.\n")
            return

        solution = session.solution
        if db_session.expiry_check(token):
            db_session.delete_session(token)
            print(f"Temps écoulé ! T'es trop lent...\nLa solution était {solution}\n")
            return

        print("Alors, la solution ? ")
        answer = input().strip()

        if db_session.expiry_check(token):
            db_session.delete_session(token)
            print(f"Temps écoulé ! T'es trop lent...\nLa solution était {solution}\n")
            return

        if answer == session.solution:
            print(f"GG. Voila ton flag!\n{FLAG}\n")
        else:
            print("Nope...\n")

        db_session.delete_session(token)

    except Exception as e:
        print("Une erreur est survenue.. Fermeture de la connection :(\n")


if __name__ == "__main__":
    main()
