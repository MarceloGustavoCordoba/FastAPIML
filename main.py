from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel
from models.item_model import Item

app = FastAPI()


@app.get('/')
def read_root():
    return {"Hello":{"World"}}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, 'q': q}

@app.put('/item/{item_id}')
def update_item(item_id: int, item: Item):
    return {'items_name': item.name, 'item_id': item_id}

@app.post("/webhook")
def webhook():
    # Puedes realizar cualquier lógica necesaria aquí
    
    # Respuesta con código de estado 200
    return {"message": "OK"}