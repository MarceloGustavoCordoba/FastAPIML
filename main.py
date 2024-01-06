from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app=FastAPI()


class Libro(BaseModel):
    titulo: str
    autor: str
    paginas: int
    editorial: Optional[str]


@app.get("/")
def index():
    return "Hola a todos"

@app.get("/Libros/{id}")
def mostrar_libros(id):
    return {"data":id}

@app.post("/libros")
def insertar_libro(libro: Libro):
    return {"message": f"libro {libro.titulo} insertado"}