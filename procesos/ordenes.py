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

def consulta_historica(parametros):
    conn_str = database.conexion()
    try:
        respuestas=[]
        total = 0
        parametros.offset = 0
        while parametros.fecha_desde <= parametros.fecha_hasta:
            while parametros.offset <= total:
                response = funciones_ml.ordenes(parametros)
                total = json.loads(response.text)['paging']['total']
                respuestas.append(response)
                parametros.offset+=parametros.limit
            parametros.offset = 0
            parametros.fecha_desde = parametros.fecha_desde + timedelta(days=1)

        respuestas_convertidas=[]
        for resp in respuestas:
            for resul in json.loads(resp.text)['results']:
                respuestas_convertidas.append(resul)

        ordenes_historicas = json_normalize(respuestas_convertidas)[['id','last_updated','shipping.id','seller.id']].rename(columns=lambda x: x.replace('.', '_')).drop_duplicates(subset='id',keep='first')
        engine = create_engine(conn_str)
        query_duplicados = f"SELECT id FROM ordenes_historial WHERE seller_id = {parametros.user_id} and id IN ({','.join(map(str, ordenes_historicas['id'].tolist()))})"
        duplicados = pd.read_sql(query_duplicados, engine)
        ordenes_nuevos = ordenes_historicas[~ordenes_historicas['id'].isin(duplicados['id'])].drop_duplicates(subset='id', keep='first')
        ordenes_nuevos.to_sql('ordenes_historial', engine, index=False, if_exists='append')
    except Exception as e:
        traza_pila = traceback.format_exc()
        logging.error(f"Error en consulta_historica: {e}\n{traza_pila}")
        raise 
    
def correr_carga_ordenes(parametros):
    conn_str = database.conexion()
    engine = create_engine(conn_str)
    query_ordenes = f'select ordenes_historial.id from ordenes_historial left join orders on ordenes_historial.id = orders.id where ordenes_historial.seller_id = {parametros.user_id} and orders.id isnull limit 1000'
    ordenes_a_cargar = pd.read_sql(query_ordenes, engine)
    cont_a = 0
    while len(ordenes_a_cargar)>0:
        cont=0
        print(cont_a)
        lista = []
        for index, row in ordenes_a_cargar.iterrows():
            parametros.order_id = row['id']
            consulta_orden = funciones_ml.consulta_orden(parametros)
            lista.append(consulta_orden)
            cont+=1
            print (f'proceso... {cont}',end='\r')
        cont_a +=1
        lista_convertida = []
        for lis in lista:
            lista_convertida.append(json.loads(lis.text))
        
        orders = json_normalize(lista_convertida).drop(columns=['order_items','payments','mediations']).rename(columns=lambda x: x.replace('.', '_'))
        payments = json_normalize(lista_convertida,'payments').rename(columns=lambda x: x.replace('.', '_'))
        order_items = json_normalize(lista_convertida,'order_items','id',meta_prefix='order_').drop(columns='item.variation_attributes').rename(columns=lambda x: x.replace('.', '_'))                

        engine = create_engine(conn_str)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            with session.begin(): 
                orders.to_sql('orders', engine, index=False, if_exists='append')
                payments.to_sql('payments', engine, index=False, if_exists='append')
                order_items.to_sql('order_items', engine, index=False, if_exists='append')
            
        except Exception as e:
            session.rollback()
            traza_pila = traceback.format_exc()
            logging.error(f"Error en cargar_detalle_orden: {e}\n{traza_pila}")    
            raise
        finally:
            session.close()
        
        time.sleep(10)  
        
        engine = create_engine(conn_str)
        query_ordenes = f'select ordenes_historial.id from ordenes_historial left join orders on ordenes_historial.id = orders.id where ordenes_historial.seller_id = {parametros.user_id} and orders.id isnull limit 1000'
        ordenes_a_cargar = pd.read_sql(query_ordenes, engine)