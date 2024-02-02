from database import database
from mercadolibre import funciones_ml
import json
import psycopg2

class Parametros:
    def __init__(self, app_id=None, client_secret=None, code=None, redirect_uri=None,
                 code_verifier=None, access_token=None, refresh_token=None, user_id=None,
                 fecha_desde=None, fecha_hasta=None, offset=0, limit=50, order_id=None,
                 shipping_id=None, site=None, price=None, inventory_id=None, 
                 max_reintentos=5,conn_str=None,status_actualizacion=None,vencimiento_token=None):
        self.app_id = app_id
        self.client_secret = client_secret
        self.code = code
        self.redirect_uri = redirect_uri
        self.code_verifier = code_verifier
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.offset = offset
        self.limit = limit
        self.order_id = order_id
        self.shipping_id = shipping_id
        self.site = site
        self.price = price
        self.inventory_id = inventory_id
        self.max_reintentos = max_reintentos
        self.conn_str = conn_str
        self.status_actualizacion = status_actualizacion
        self.vencimiento_token = vencimiento_token


class ClienteNuevo():
    
    def __init__(self,site,code):
        
        self.code = None
        
        self.code_verifier = None
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.db = HandleDB()
        self.site = site
        self.code = code
    
    def datos_app(self):
        datos = self.db.cargar_app()
        self.app_id = datos[0]
        self.client_secret = datos[1]
        self.redirect_uri = datos[2]
    
    def token(self):
        respuesta = funciones_ml.get_token(self)
        respuesta = json.loads(respuesta.text)
        
        self.access_token=respuesta['access_token']
        self.user_id=respuesta['user_id']
        self.refresh_token=respuesta['refresh_token']          


class HandleDB():
    def __init__(self):
        conn_str = database.conexion()
        self._con = psycopg2.connect(conn_str)
        self._cur = self._con.cursor()

        # Asegúrate de tener la tabla 'users' creada en tu base de datos PostgreSQL con la misma estructura.

    def cargar_app(self):
        self._cur.execute(f"select app_id, client_secret, uri from aplicaciones where site = 'MLA'")
        data = self._cur.fetchone()
        return data
    
    def consulta_cliente(self,user_id):
        self._cur.execute(f"select count(*) from conexion_clientes where user_id = {user_id}")
        data = self._cur.fetchone()
        return data

    def get_only(self, data_user):
        self._cur.execute("SELECT * FROM users WHERE username = %s", (data_user,))
        data = self._cur.fetchone()
        return data

    def insert(self, data_user):
        self._cur.execute(
            "INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s)",
            (
                data_user["id"],
                data_user["firstname"],
                data_user["lastname"],
                data_user["username"],
                data_user["country"],
                data_user["password_user"]
            )
        )
        self._con.commit()

    def __del__(self):
        self._con.close()
