from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from procesos import notificaciones
import logging
import pandas as pd
from sqlalchemy import create_engine,text
import os
import json
import sys 

app = FastAPI()
carpeta_logs = 'logs'
if not os.path.exists(carpeta_logs):
    os.makedirs(carpeta_logs)

ruta_archivo_log = os.path.join(carpeta_logs, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=ruta_archivo_log, level=logging.ERROR)
    
@app.get('/')
def read_root():
    return "Proceso Completo."

@app.post('/MLA_callbacks')
async def webhook(request: Request):
    try:
        payload= await request.json()
        load = notificaciones.insert_notification(payload)
        if load == 200:
            return JSONResponse(content={'message': 'OK'}, status_code=200)
    except Exception as e:
        logging.error(f'Error al procesar la notificación: {e}')
        raise HTTPException(status_code=500, detail='Internal Server Error')

# modificar para que al autorizar un cliente nuevo lea el codigo y realice el regitro en la bbdd de la base de datos y comienze a poblar la bbdd
@app.get('/MLA_redirect')
async def redireccionamiento(code: str = Query(...)):
    return {"codigo de redireccionamiento" : code}