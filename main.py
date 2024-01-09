from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from database import database_utils as db
import logging
import pandas as pd
from sqlalchemy import create_engine,text

app = FastAPI()
logging.basicConfig(filename='app.log', level=logging.DEBUG)
                
@app.get('/')
def read_root():
    return "Proceso Completo."

@app.post('/callbacks')
async def webhook(request: Request):
    try:
        payload= await request.json()
        print(payload)
        db.insert_notification(payload)
        return JSONResponse(content={'message': 'OK'}, status_code=200)
    except Exception as e:
        logging.error(f'Error al procesar la notificación: {e}')
        raise HTTPException(status_code=500, detail='Internal Server Error')