from sqlalchemy import Column, String, Integer, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta

Base = declarative_base()

class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer)
    operation_number = Column(Integer)
    instructions = Column(LargeBinary)

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    solution = Column(String)
    expiry = Column(DateTime)
    start_buffer_values = Column(LargeBinary)
    current_operation_number = Column(Integer, default=0)
    current_verification = Column(Integer, default=0)
    received_all_operations = Column(Integer, default=0)

class Database:
    def __init__(self, engine, token_validity_duration, token_deleted_after):
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.session = session
        self.token_validity_duration = token_validity_duration
        self.token_deleted_after = token_deleted_after
    
    def __del__(self):
        self.session.close()

    def create_session(self, token, solution, start_buffer_values=None):
        if self.get_session(token):
            return False
        new_entry = Session(
            token=token,
            solution=solution,
            expiry=datetime.now()+timedelta(seconds=self.token_validity_duration),
            start_buffer_values=start_buffer_values
        )
        self.session.add(new_entry)
        self.session.commit()
        return True

    def get_session(self, token):
        session = self.session.query(Session).filter_by(token=token).first()
        if not session:
            return None
        return session

    def delete_session(self, token):
        session = self.session.query(Session).filter_by(token=token).first()
        if session:
            self.session.query(Operation).filter_by(session_id=session.id).delete()
            self.session.delete(session)
            self.session.commit()
            return True
        return False

    def expiry_check(self, token):
        session = self.session.query(Session).filter_by(token=token).first()
        if not session or session.expiry < datetime.now():
            return True
        return False
    
    def add_operation(self, token, instructions, operation_number):
        session = self.get_session(token)
        if not session:
            return False
        new_operation = Operation(
            session_id=session.id,
            operation_number=operation_number,
            instructions=instructions
        )
        self.session.add(new_operation)
        self.session.commit()
        return True

    def get_operation(self, token):
        session = self.get_session(token)
        if not session:
            return None
        operation = self.session.query(Operation).filter_by(session_id=session.id, operation_number=session.current_operation_number).first()
        if not operation:
            return None
        session.current_operation_number += 1
        self.session.commit()
        return operation
    
    def clean_sessions(self):
        total_sessions = len(self.session.query(Session).all())
        print(f"Total sessions: {total_sessions}")
        expired_sessions = self.session.query(Session).filter(Session.expiry < datetime.now()-timedelta(seconds=self.token_deleted_after)).all()
        for session in expired_sessions:
            self.delete_session(session.token)

    def get_current_prompt_and_start_buffer(self, token):

        MESSAGES = [
            "Veuillez fournir votre clé de vérification.\nClé : ",
            "Mouais.. Tout le monde peut la deviner.. J'ai besoin d'une deuxième vérification.\nClé : ",
            "Une dernière vérification pour la route. On est jamais trop prudent, hein ?\nClé : "
        ]

        session = self.get_session(token)
        if not session:
            return None
        
        verif_num = session.current_verification

        if verif_num == len(MESSAGES):
            return "done", b'\x00'*16

        message = MESSAGES[verif_num]
        start_buffer_value = session.start_buffer_values[16*verif_num:16*(verif_num+1)]
        session.current_verification += 1
        self.session.commit()
        return message, start_buffer_value
    
    def set_received_all_operations(self, token):
        session = self.get_session(token)
        if not session:
            return False
        session.received_all_operations = 1
        self.session.commit()
        return True