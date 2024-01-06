from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel
from models.item_model import Item
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import json
from ftplib import FTP
from datetime import datetime
import io

app = FastAPI()

# Configuración del servidor FTP
FTP_HOST = 'srva194.controlvps.com'
FTP_USER = 'marcelocordoba'
FTP_PASSWORD = 'Hudson.2024!'
FTP_REMOTE_FOLDER = '/marcelo/Marcor/notificaciones'

@app.get('/')
def read_root():
    return {"Hello":{"World"}}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, 'q': q}

@app.put('/item/{item_id}')
def update_item(item_id: int, item: Item):
    return {'items_name': item.name, 'item_id': item_id}

@app.post('/webhook')
async def webhook(request: Request):
    try:
        # Obtener el contenido JSON de la notificación
        notification_data = await request.json()

        # Crear un nombre de archivo único basado en la fecha y hora
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename = f'{timestamp}_notification.json'

        # Crear un objeto de tipo bytes en memoria
        in_memory_file = io.BytesIO(json.dumps(notification_data, indent=2).encode('utf-8'))

        # Conectar al servidor FTP y cargar el archivo directamente desde la memoria
        with FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASSWORD)
            ftp.cwd(FTP_REMOTE_FOLDER)

            ftp.storbinary(f'STOR {filename}', in_memory_file)

        print(f'Notificación cargada en el servidor FTP en {FTP_REMOTE_FOLDER}/{filename}')

        return JSONResponse(content={'message': 'success'}, status_code=200)

    except Exception as e:
        print(f'Error al procesar la notificación: {e}')
        raise HTTPException(status_code=500, detail='Internal Server Error')
