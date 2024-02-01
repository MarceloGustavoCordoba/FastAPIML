from mercadolibre import utils,funciones_ml
from datetime import datetime,timedelta
from models import clases
import pandas as pd
import json
import os
import logging

from pandas import json_normalize
from database import database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)

# Configurar el logger
ruta_archivo_log = os.path.join(carpeta_logs, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.ERROR)

def publicidad(parametros):
    ## campañas
    # 
    total = 0 
    campañas_lista = []
    parametros.offset=0
    while parametros.offset <= total:
        respuesta = funciones_ml.campañas_usuario(parametros)
        if respuesta.status_code == 200:
            campañas_lista.append(respuesta)
            parametros.offset+=parametros.limit
            total = json.loads(respuesta.text)['paging']['total']
        else:
            break

    campañas_conv   = []
    for elemento in campañas_lista:
        campañas_conv.append(json.loads(elemento.text))
    campañas = json_normalize(campañas_conv,'results').rename(columns=lambda x: x.replace('.','_'))

    ## anuncios
    anuncios_lista = []
    total = 0 
    parametros.offset=0
    while parametros.offset <= total:
        respuesta = funciones_ml.anuncios(parametros,'marketplace')
        if respuesta.status_code == 200:
            anuncios_lista.append(respuesta)
            parametros.offset+=parametros.limit
            total = json.loads(respuesta.text)['paging']['total']
        else:
            break

    total = 0 
    parametros.offset=0
    while parametros.offset <= total:
        respuesta = funciones_ml.anuncios(parametros,'mshops')
        if respuesta.status_code == 200:
            anuncios_lista.append(respuesta)
            parametros.offset+=parametros.limit
            total = json.loads(respuesta.text)['paging']['total']
        else:
            break

    anuncios_conv   = []
    for elemento in anuncios_lista:
        anuncios_conv.append(json.loads(elemento.text))
        
    anuncios = json_normalize(anuncios_conv,'results')
    anuncios = anuncios[anuncios['campaign_id'] !=0].reset_index(drop=True)
    
    resultados = []
    for index, row in anuncios.iterrows():
        campaña = row['campaign_id']
        MLA = row['id']
        if campaña != 0:
            fecha_limite=parametros.fecha_hasta-timedelta(days=90)
            fecha_inicial = parametros.fecha_hasta-timedelta(days=1)
            general = funciones_ml.metrica_anuncio(parametros,campaña,fecha_limite,fecha_inicial,MLA)
            cont_gral=0
            for ele in list(json.loads(general.text)[0].values()):
                if type(ele) != str:
                    cont_gral+=ele
            if cont_gral > 0:    
                while fecha_inicial >= fecha_limite:
                    metrica = funciones_ml.metrica_anuncio(parametros,campaña,fecha_inicial,fecha_inicial,MLA)
                    cont=0
                    for ele in list(json.loads(metrica.text)[0].values()):
                        if type(ele) != str:
                            cont+=ele
                    if cont > 0:
                        registro = {
                            "campaña": campaña,
                            "fecha": fecha_inicial.strftime('%Y-%m-%d'),
                            "data": json.loads(metrica.text)[0]  
                        }
                        resultados.append(registro)
                    fecha_inicial=fecha_inicial-timedelta(days=1)
    
    metricas_anuncios = json_normalize(resultados).rename(columns=lambda x: x.replace('.','_'))
    
    conn_str = database.conexion()
    engine = create_engine(conn_str)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin(): 
            campañas.to_sql('campañas', engine, index=False, if_exists='append')
            anuncios.to_sql('anuncios', engine, index=False, if_exists='append')
            metricas_anuncios.to_sql('metricas_anuncios', engine, index=False, if_exists='append')
            
    except Exception as e:
        session.rollback()
        traza_pila = traceback.format_exc()
        logging.error(f"Error en cargar_detalle_orden: {e}\n{traza_pila}")    
        raise
    finally:
        session.close()