from database import database
from mercadolibre import funciones_ml
import pandas as pd
from sqlalchemy import create_engine
from models import clases

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
    
    return{"codigo de redireccionamiento:" : code,
           "Site:" : site,
           "resp: ": respuesta}