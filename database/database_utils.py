import os
import pandas as pd
from sqlalchemy import create_engine,text
import logging

def execute_query_as_dataframe(query):
    conn_str = os.getenv("DATABASE_URL")
    engine = create_engine(conn_str)
    
    try:
        result_df = pd.read_sql_query(query, engine)
        return result_df
    finally:
        engine.dispose()
        
        
def insert_notification(data):
    conn_str = os.getenv("DATABASE_URL")
    
    if conn_str is None:
        raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
    
    engine = create_engine(conn_str)
    
    try:
        with engine.connect() as connection:
            insert_query = text("""
                INSERT INTO notificaciones (_id, topic, resource, user_id, application_id, sent, attempts, received)
                VALUES (:id, :topic, :resource, :user_id, :application_id, :sent, :attempts, :received)
            """)
            connection.execute(insert_query, **data)
    except Exception as e:
        logging.error(f'Error al insertar notificación en la base de datos: {e}')
    finally:
        engine.dispose()

