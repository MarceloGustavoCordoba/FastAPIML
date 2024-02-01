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

        