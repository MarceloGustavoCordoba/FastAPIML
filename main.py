from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel
from models.item_model import Item
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import psycopg2
from psycopg2 import sql

app = FastAPI()

def get_db_connection():
    # Devuelve una conexión a la base de datos (asegúrate de proporcionar los valores correctos)
    conn = psycopg2.connect(
        dbname='mercadolibre',
        user='sa',
        password='ZcdcuIMgzdD3vnO58UW3h0Ra0UpSjfaE',
        host='dpg-cmcrgdn109ks7392qm4g-a.oregon-postgres.render.com',
        port='5432'
    )
    return conn

def insert_notification(data):
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO notifications (_id, topic, resource, user_id, application_id, sent, attempts, received)
            VALUES (%(_id)s, %(topic)s, %(resource)s, %(user_id)s, %(application_id)s, %(sent)s, %(attempts)s, %(received)s)
        """
        cursor.execute(insert_query, data)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
        
@app.get('/')
def read_root():
    return "Proceso Completo."

@app.post('/callbacks')
async def webhook(request: Request):
    try:
        # Obtener el contenido JSON de la notificación
        notification_data = await request.json()
        insert_notification(notification_data)

        return JSONResponse(content={'message': 'OK'}, status_code=200)

    except Exception as e:
        print(f'Error al procesar la notificación: {e}')
        raise HTTPException(status_code=500, detail='Internal Server Error')
