import traceback, logging
from pandas import json_normalize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from database import database


def insert_notification(notificacion):
    session = None
    
    try:
        noti_df = json_normalize(notificacion)
        conn_str = database.conexion()
        engine = create_engine(conn_str)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        with session.begin(): 
            noti_df.to_sql('notificaciones', engine, index=False, if_exists='append')
            return 200
    except Exception as e:
        if session is not None:
            session.rollback()
        traza_pila = traceback.format_exc()
        logging.error(f"Error en cargar_detalle_orden: {e}\n{traza_pila}")    
        raise
    finally:
        if session is not None:
            session.close()