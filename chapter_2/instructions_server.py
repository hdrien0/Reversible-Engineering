#Author : _hdrien
#404CTF 2024

import sys

from sqlalchemy import create_engine
from db import Database
import os

TOKEN_VALIDITY_DURATION = os.getenv('TOKEN_VALIDITY_DURATION', 600)
TOKEN_DELETED_AFTER = os.getenv('TOKEN_DELETED_AFTER', 900)

engine = create_engine('sqlite:///tokens.db')

def main():

    try:
        db_session = Database(engine, TOKEN_VALIDITY_DURATION, TOKEN_DELETED_AFTER)
        token = input().strip()
        session = db_session.get_session(token)
        if not session:
            return
        
        operation = db_session.get_operation(token)

        if not operation :
            if session.received_all_operations == 0:
                sys.stdout.buffer.write(b"endfunc")
                sys.stdout.buffer.flush()
                db_session.set_received_all_operations(token)
                return
            prompt, start_buffer_value = db_session.get_current_prompt_and_start_buffer(token)
            sys.stdout.buffer.write(start_buffer_value)
            sys.stdout.buffer.flush()
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return
        
        else:
            sys.stdout.buffer.write(operation.instructions)
            sys.stdout.buffer.flush()
            sys.stdout.buffer.write(b"endfunc")
            sys.stdout.buffer.flush()
            return

    except Exception as e:
        return


if __name__ == "__main__":
    main()
