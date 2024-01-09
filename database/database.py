import os
import pandas as pd
from sqlalchemy import create_engine,text
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.bd_mercadolibre import Base, Notificacion
from datetime import datetime

def execute_query_as_dataframe(query):
    conn_str = os.getenv("DATABASE_URL")
    engine = create_engine(conn_str)
    
    try:
        result_df = pd.read_sql_query(query, engine)
        return result_df
    finally:
        engine.dispose()
        
def init_db(conn_str):
    engine = create_engine(conn_str)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def insert_notification(data):

    try:
        session = init_db(os.getenv("DATABASE_URL"))
    
        nueva_notificacion = Notificacion(
            _id=data["_id"],
            topic=data["topic"],
            resource=data["resource"],
            user_id=data["user_id"],
            application_id=data["application_id"],
            sent=datetime.strptime(data["sent"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            attempts=data["attempts"],
            received=datetime.strptime(data["received"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            actions=data["actions"],
            revisado=False
        )
        session.add(nueva_notificacion)
        session.commit()
    
    except Exception as e:
        print(f"Error al insertar notificación: {e}")
    finally:
        if session: 
            session.close()
