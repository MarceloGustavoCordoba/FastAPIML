from database import database
from datetime import datetime, timedelta
from mercadolibre import funciones_ml
import json
import traceback
from models import clases
import os

## verifica si el token de un cliente esta vencido
def token_vencido(parametros):

    query='select vencimiento_token from conexion_clientes where user_id=' + str(parametros.user_id)
    vencimiento=database.execute_query_as_list(query,parametros.conn_str)
    vencido = vencimiento[0][0].time()<datetime.now().time()
    return vencido

## devuelve objeto parametros con el nuevo access_token y refresh token, ademas de actualizar los mismos en la base de datos
def actualizacion_token(parametros):
    try:
        nuevo_token = funciones_ml.refresh_token(parametros)
        if nuevo_token.status_code == 200:
            nuevo_token=json.loads(nuevo_token.text)
            parametros.access_token = nuevo_token['access_token']
            parametros.refresh_token = nuevo_token['refresh_token']
            parametros.vencimiento_token=((datetime.combine(datetime.today(), (datetime.now().time()))) + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
            query = "UPDATE conexion_clientes SET access_token = '" + str(parametros.access_token) + "', refresh_token = '" + str(parametros.refresh_token) + "', vencimiento_token = '" + parametros.vencimiento_token + "' WHERE user_id = '" + str(parametros.user_id) + "';"
            database.execute_update_query(query, parametros.conn_str)
            parametros.status_actualizacion = 200
        else:
            parametros.status_actualizacion = nuevo_token.status_code
    except Exception as e:
        traceback.print_exc() 
        return e

def gen_parametros(user_id, conn_str=None):
    parametros = clases.Parametros()

    parametros.user_id = user_id
    parametros.conn_str=database.conexion()
        
    query="select app_id, code, access_token, refresh_token, vencimiento_token from conexion_clientes where user_id=" + str(parametros.user_id)
    conexion_clientes=database.execute_query_as_list(query,parametros.conn_str)
    parametros.app_id=conexion_clientes[0][0]
    parametros.code = conexion_clientes[0][1]
    parametros.access_token = conexion_clientes[0][2]
    parametros.refresh_token = conexion_clientes[0][3]
    parametros.vencimiento_token = conexion_clientes[0][4]
    query="select site, client_secret, uri from aplicaciones where app_id=" + str(parametros.app_id)
    aplicaciones=database.execute_query_as_list(query,parametros.conn_str)
    parametros.site=aplicaciones[0][0]
    parametros.client_secret = aplicaciones[0][1]
    parametros.redirect_uri = aplicaciones[0][2]
    parametros.fecha_desde=(datetime.today() - timedelta(days=366))
    parametros.fecha_hasta=datetime.today()
    
    return parametros