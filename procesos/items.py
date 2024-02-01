from mercadolibre import funciones_ml
import json
from pandas import json_normalize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import database
import traceback, logging

def cargar_items(parametros):
    conn_str = database.conexion()
    respuestas=[]
    total = 0
    parametros.offset = 0
    while parametros.offset <= total:
        response = funciones_ml.user_items(parametros,'active')
        total = json.loads(response.text)['paging']['total']
        respuestas.append(response)
        parametros.offset+=parametros.limit

    total = 0
    parametros.offset = 0
    while parametros.offset <= total:
        response = funciones_ml.user_items(parametros,'paused')
        total = json.loads(response.text)['paging']['total']
        respuestas.append(response)
        parametros.offset+=parametros.limit

    total = 0
    parametros.offset = 0
    while parametros.offset <= total:
        response = funciones_ml.user_items(parametros,'pending')
        total = json.loads(response.text)['paging']['total']
        respuestas.append(response)
        parametros.offset+=parametros.limit

    total = 0
    parametros.offset = 0
    while parametros.offset <= total:
        response = funciones_ml.user_items(parametros,'not_yet_active')
        total = json.loads(response.text)['paging']['total']
        respuestas.append(response)
        parametros.offset+=parametros.limit

    total = 0
    parametros.offset = 0
    while parametros.offset <= total:
        response = funciones_ml.user_items(parametros,'programmed')
        total = json.loads(response.text)['paging']['total']
        respuestas.append(response)
        parametros.offset+=parametros.limit

    total = 0
    parametros.offset = 0
    while parametros.offset <= total:
        response = funciones_ml.user_items(parametros,'closed')
        total = json.loads(response.text)['paging']['total']
        respuestas.append(response)
        parametros.offset+=parametros.limit
        
    respuestas_convertidas=[]
    for resp in respuestas:
        for resul in json.loads(resp.text)['results']:
            respuestas_convertidas.append(resul)

    items = []
    for resp in respuestas_convertidas:
        items.append(json.loads(funciones_ml.item_details(parametros,resp).text))

    bodys = []
    for it in items:
        bodys.append(it[0]['body'])

    items_df = json_normalize(bodys).drop(columns=['variations','attributes']).rename(columns=lambda x: x.replace('.', '_'))
    atributos = json_normalize(bodys,'attributes','id',meta_prefix='item_').pivot_table(values='value_name',columns='name',index='item_id',aggfunc=lambda x: x.iloc[0]).reset_index()[['item_id','Marca','Modelo','SKU']]
    variaciones = json_normalize(bodys,'variations','id',meta_prefix='item_').drop(columns=['item_relations','attribute_combinations','picture_ids',])

    items_df.drop_duplicates('id',inplace=True)
    variaciones.drop_duplicates('id',inplace=True)

    engine = create_engine(conn_str)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin(): 
            items_df.to_sql('items', engine, index=False, if_exists='append')
            atributos.to_sql('atributos', engine, index=False, if_exists='append')    
            variaciones.to_sql('variaciones', engine, index=False, if_exists='append')
            return 200
    except Exception as e:
        session.rollback()
        traza_pila = traceback.format_exc()
        logging.error(f"Error en cargar_detalle_orden: {e}\n{traza_pila}")    
        raise
    finally:
        session.close()