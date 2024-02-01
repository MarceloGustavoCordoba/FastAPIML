import os
import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import DictCursor
from pandas import json_normalize
from sqlalchemy import create_engine,text
from pandas import json_normalize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import json
import traceback

def conexion():
    try:
        with open('db.json', 'r') as archivo_json:
            conn_str = json.load(archivo_json)
            conn_str=conn_str['conn_str']
    except FileNotFoundError:
        conn_str = os.getenv("DATABASE_URL")
    return conn_str

def conectar_base_datos(conn_str=None):
    try:
        with open('db.json', 'r') as archivo_json:
            conn_str = json.load(archivo_json)
            conn_str=conn_str['conn_str']
    except FileNotFoundError:
        conn_str = os.getenv("DATABASE_URL")
        
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(conn_str)
        return conn

    except Exception as e:
        print(f'Error al conectar a la base de datos: {e}')
        raise

def execute_query_as_dataframe(query,conn_str=None):
    
    if conn_str is None:
        conn_str = os.getenv("DATABASE_URL")
    engine = create_engine(conn_str)
    
    try:
        result_df = pd.read_sql_query(query, engine)
        return result_df
    finally:
        engine.dispose()

def execute_query_as_list(query, conn_str=None):
    conn = conectar_base_datos(conn_str)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute(query)
        result_list = cursor.fetchall()
        return result_list
    finally:
        cursor.close()
        conn.close()

def execute_update_query(query, conn_str=None):
    conn = conectar_base_datos(conn_str)
    cursor = conn.cursor(cursor_factory=DictCursor)

    try:
        cursor.execute(query)
        conn.commit()
        
    finally:
        cursor.close()
        conn.close()

def tabla_existe(nombre_tabla, cursor):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = %s
        );
    """, (nombre_tabla,))
    return cursor.fetchone()[0]

def crear_tablas(nombre_tabla, script_path, conn_str=None):
    conn = conectar_base_datos(conn_str)
    cursor = conn.cursor()
    if not tabla_existe(nombre_tabla, cursor):
        try:
            # Leer el contenido del script SQL
            with open(script_path, 'r') as file:
                script = file.read()
            cursor.execute(script)
            conn.commit()
            print(f'Se creó la tabla: {nombre_tabla}')

        except Exception as e:
            print(f'Error al crear {nombre_tabla}: {e}')
    else:
        print(f'La tabla {nombre_tabla} ya existe')

    cursor.close()
    conn.close()

