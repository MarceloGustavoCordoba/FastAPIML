from database import database
from mercadolibre import funciones_ml
import pandas as pd
from sqlalchemy import create_engine
from models import clases
import json
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

def alta_usuario(code,site):

    conn_str = database.conexion()
    query = f"select app_id, client_secret, uri from aplicaciones where site = '{site}'"
    data=database.execute_query_as_list(query,conn_str)
    
    parametros = clases.Parametros()
    
    parametros.code=code
    parametros.app_id=data[0][0]
    parametros.client_secret = data[0][1]
    parametros.redirect_uri = data[0][2]
    
    respuesta = funciones_ml.get_token(parametros)
    respuesta = json.loads(respuesta.text)
    
    parametros.access_token=respuesta['access_token']
    parametros.user_id=respuesta['user_id']
    parametros.refresh_token=respuesta['refresh_token']

    query = f"select user_id from conexion_clientes where user_id = 64657025"
    data=database.execute_query_as_list(query,conn_str)
    
    nickname = funciones_ml.users_me(parametros)
    
    nickname=json.loads(nickname.text)['nickname']
    
    if len(data) == 0:
        
    else:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define los nuevos valores que deseas actualizar
        new_values = {
            'access_token': parametros.access_token,
            'refresh_token': parametros.refresh_token,
            'nickname': nickname
        }

        # Realiza la actualización en la base de datos
        stmt = update(ConexionClientes).where(ConexionClientes.user_id == parametros.user_id).values(new_values)
        session.execute(stmt)
        session.commit()
        session.close()

    
    return{"codigo de redireccionamiento:" : code,
           "Site:" : site,
           "resp: ": respuesta.text}