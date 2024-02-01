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
    
ruta_archivo_log = os.path.join(carpeta_logs, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.ERROR)

# Consulta envios pendientes de cargarse, genera las consultas a la api y realiza la carga a la bbdd
def cargar_envios(parametros):
    
    conn_str = database.conexion()
    engine = create_engine(conn_str)
    query_ordenes = f'select distinct(orders.shipping_id) from orders left join envios on orders.shipping_id = envios.id where envios.id isnull and orders.seller_id = {parametros.user_id} limit 2000'
    envios_a_cargar = pd.read_sql(query_ordenes, engine)

    cont_a = 0 
    while len(envios_a_cargar) > 0:
        cont=0
        lista = []
        print(cont_a)
        for index, row in envios_a_cargar.iterrows():
            parametros.shipping_id = row['shipping_id']
            consulta_envio = funciones_ml.envios(parametros)
            time.sleep(2)
            lista.append(consulta_envio)
            cont+=1
            print (f'proceso... {cont}',end='\r')
        
        cont_a+=1
        
        lista_convertida = []
        for elemento in lista:
            lista_convertida.append(json.loads(elemento.text))

        envio_df = json_normalize(lista_convertida).drop(columns=['substatus_history','shipping_items']).rename(columns=lambda x: x.replace('.', '_'))

        engine = create_engine(conn_str)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            with session.begin(): 
                envio_df.to_sql('envios', engine, index=False, if_exists='append')
        except Exception as e:
            session.rollback()
            traza_pila = traceback.format_exc()
            logging.error(f"Error en cargar_detalle_orden: {e}\n{traza_pila}")    
            raise
        finally:
            session.close()
                
        engine = create_engine(conn_str)
        query_ordenes = f'select distinct(orders.shipping_id) from orders left join envios on orders.shipping_id = envios.id where envios.id isnull and orders.seller_id = {parametros.user_id} limit 1000'
        envios_a_cargar = pd.read_sql(query_ordenes, engine)









