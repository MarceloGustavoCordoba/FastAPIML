from database import database
from mercadolibre import funciones_ml
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from pandas import json_normalize
import os, logging, traceback, json
from sqlalchemy.orm import sessionmaker
import time

carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)

# Configurar el logger
ruta_archivo_log = os.path.join(carpeta_logs, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.ERROR)

def preguntas(parametros):
    conn_str = database.conexion()
    try:
        engine = create_engine(conn_str)
        query_ordenes = f"select id from items where status = 'active' and seller_id = {parametros.user_id}"
        items = pd.read_sql(query_ordenes, engine)
        
        lista = []
        for index, row in items.iterrows():
            item = row['id']
            lista.append(funciones_ml.preg_resp(parametros,item))
        
        lista_convertida = []
        for respuesta in lista:
            lista_convertida.append(json.loads(respuesta.text))
        
        lista_convertida = [elemento for elemento in lista_convertida if len(elemento) != 0]
        
        preguntas = json_normalize(lista_convertida,'questions').rename(columns=lambda x: x.replace('.', '_'))
        
        
        engine = create_engine(conn_str)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            with session.begin(): 
                preguntas.to_sql('preguntas', engine, index=False, if_exists='append')
                return 200
        except Exception as e:
            session.rollback()
            traza_pila = traceback.format_exc()
            raise
        finally:
            session.close()
    except Exception as e:
        logging.error(f"Error en preguntas: {e}\n{traza_pila}")    
        raise