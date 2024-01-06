from fastapi import FastAPI
import uvicorn
import pandas as pd
import json as json

class MovieAnalyzer:

    def cantidad_filmaciones_mes(self, mes: str):
        """
        Devuelve la cantidad de filmaciones realizadas en un mes específico.

        Args:
            mes (str): El nombre del mes.

        Returns:
            dict: Un diccionario con el nombre del mes y la cantidad de filmaciones.

        """
        # Convertir el nombre del mes a minúsculas
        mes = mes.lower()

        # Asignar el número correspondiente al mes
        meses_dict = {
            'enero': '01',
            'febrero': '02',
            'marzo': '03',
            'abril': '04',
            'mayo': '05',
            'junio': '06',
            'julio': '07',
            'agosto': '08',
            'septiembre': '09',
            'octubre': '10',
            'noviembre': '11',
            'diciembre': '12'
        }
        mes_numero = meses_dict.get(mes)

        # Verificar si el mes es válido
        if mes_numero:
            # Convertir la columna 'release_date' a tipo string
            df_movies_norm['release_date'] = df_movies_norm['release_date'].dt.strftime('%Y-%m-%d')

            # Filtrar las filas del DataFrame que corresponden al mes consultado
            filtrado = df_movies_norm[df_movies_norm['release_date'].str[5:7] == mes_numero]

            # Obtener la cantidad de películas estrenadas en el mes
            cantidad = len(filtrado)

            # Retornar el resultado
            return {'mes': mes, 'cantidad': cantidad}
        else:
            return {'error': f'El mes "{mes}" no es válido.'}

    def cantidad_filmaciones_dia(self, dia: str):
        """
        Devuelve la cantidad de filmaciones realizadas en un día de la semana específico.

        Args:
            dia (str): El nombre del día.

        Returns:
            dict: Un diccionario con el nombre del día y la cantidad de filmaciones.

        """
        # Convertir el nombre del día a minúsculas
        dia = dia.lower()

        # Asignar el número correspondiente al día de la semana
        dias_dict = {
            'lunes': 0,
            'martes': 1,
            'miércoles': 2,
            'jueves': 3,
            'viernes': 4,
            'sábado': 5,
            'domingo': 6
        }
        dia_numero = dias_dict.get(dia)

        # Verificar si el día es válido
        if dia_numero is not None:
            # Convertir la columna 'release_date' a tipo datetime
            df_movies_norm['release_date'] = pd.to_datetime(df_movies_norm['release_date'])

            # Filtrar las filas del DataFrame que corresponden al día consultado
            filtrado = df_movies_norm[df_movies_norm['release_date'].dt.dayofweek == dia_numero]

            # Obtener la cantidad de películas estrenadas en el día
            cantidad = len(filtrado)

            # Retornar el resultado
            return {'día': dia, 'cantidad': cantidad}
        else:
            return f'El día "{dia}" no es válido.'

    def score_titulo(self, titulo: str):
        """
        Devuelve la información de las películas con un título específico.

        Args:
            titulo (str): El título de la película.

        Returns:
            list: Una lista con la información de las películas encontradas.

        """
        # Convertir el título a minúsculas
        titulo = titulo.lower()

        # Filtrar las películas por título en el DataFrame df_movies_norm (comparación insensible a mayúsculas y minúsculas)
        filtrado = df_movies_norm[df_movies_norm['title'].str.lower() == titulo]

        # Verificar si se encontraron películas
        if len(filtrado) > 0:
            resultados = []
            for index, row in filtrado.iterrows():
                # Obtener el año de estreno y el score/popularidad de cada película
                anio = row['release_year']
                popularidad = row['popularity']

                # Agregar el resultado a la lista de resultados
                resultados.append({'titulo': row['title'], 'anio': anio, 'popularidad': popularidad})

            # Retornar la lista de resultados
                return resultados
        else:
            return f'No se encontró ninguna película con título "{titulo}" en el dataset.'

    def votos_titulo(self, titulo: str):
        """
        Devuelve la información de votos de una película específica.

        Args:
            titulo (str): El título de la película.

        Returns:
            dict: Un diccionario con la información de votos de la película.

        """        
        # Convertir el título a minúsculas
        titulo = titulo.lower()

        # Filtrar las películas por título en el DataFrame df_movies_norm (comparación insensible a mayúsculas y minúsculas)
        filtrado = df_movies_norm[df_movies_norm['title'].str.lower() == titulo]

        # Verificar si se encontró la película
        if len(filtrado) > 0:
            votos_total = filtrado.iloc[0]['vote_count']
            voto_promedio = filtrado.iloc[0]['vote_average']

            # Verificar si tiene al menos 2000 valoraciones
            if votos_total >= 2000:
                return {'titulo': filtrado.iloc[0]['title'], 'voto_total': votos_total, 'voto_promedio': voto_promedio}
            else:
                return f'La película "{filtrado.iloc[0]["title"]}" no cumple con la condición de tener al menos 2000 valoraciones.'
        else:
            return f'No se encontró ninguna película con título "{titulo}" en el dataset.'
            
    def get_actor(self, nombre_actor: str):
        """
        Devuelve la información de un actor específico.

        Args:
            nombre_actor (str): El nombre del actor.

        Returns:
            dict: Un diccionario con la información del actor.

        """        
        # Convertir el nombre del actor a minúsculas
        nombre_actor = nombre_actor.lower()

        # Filtrar el DataFrame df_credits_norm por el nombre del actor y el trabajo 'Actor' (comparación insensible a mayúsculas y minúsculas)
        filtrado = df_credits_norm[(df_credits_norm['name'].str.lower() == nombre_actor) & (df_credits_norm['job'] == 'Actor')]

        # Obtener la cantidad de filmaciones del actor
        cantidad_filmaciones = len(filtrado)

        # Verificar si el actor ha participado en al menos una filmación
        if cantidad_filmaciones > 0:
            # Obtener los créditos de las filmaciones del actor
            creditos_actor = filtrado['credits_id'].unique()

            # Filtrar el DataFrame df_movies_norm por los créditos del actor
            peliculas_actor = df_movies_norm[df_movies_norm['id'].isin(creditos_actor)]

            # Calcular el retorno total y el promedio de retorno excluyendo las filmaciones con retorno igual a cero
            retorno_total = peliculas_actor['return'].sum().round(2)
            cantidad_filmaciones_retorno = len(peliculas_actor[peliculas_actor['return'] != 0])
            retorno_promedio = (retorno_total / cantidad_filmaciones_retorno).round(2)

            return {'actor': nombre_actor, 'cantidad_filmaciones': cantidad_filmaciones, 'retorno_total': retorno_total, 'retorno_promedio': retorno_promedio}
        else:
            return f'No se encontró ninguna filmación para el actor "{nombre_actor}" en el dataset.'

    def get_director(self, nombre_director: str):
        """
        Devuelve la información de un director específico.

        Args:
            nombre_director (str): El nombre del director.

        Returns:
            dict: Un diccionario con la información del director.

        """
        # Convertir el nombre del director a minúsculas
        nombre_director = nombre_director.lower()

        # Filtrar el DataFrame df_credits_norm por el nombre del director y el trabajo 'Director' (comparación insensible a mayúsculas y minúsculas)
        filtrado = df_credits_norm[(df_credits_norm['name'].str.lower() == nombre_director) & (df_credits_norm['job'] == 'Director')]

        # Obtener la cantidad de filmaciones del director
        cantidad_filmaciones = len(filtrado)

        # Verificar si el director ha dirigido al menos una película
        if cantidad_filmaciones > 0:
            # Obtener los créditos de las filmaciones del director
            creditos_director = filtrado['credits_id'].unique()

            # Filtrar el DataFrame df_movies_norm por los créditos del director
            peliculas_director = df_movies_norm[df_movies_norm['id'].isin(creditos_director)]

            # Calcular el éxito total del director
            retorno_total_director = peliculas_director['return'].sum().round(2)

            # Crear una lista para almacenar la información de cada película
            peliculas_info = []

            # Recorrer cada película del director
            for index, pelicula in peliculas_director.iterrows():
                info_pelicula = {
                    'titulo': pelicula['title'],
                    'fecha_lanzamiento': pelicula['release_date'].strftime('%Y-%m-%d'),
                    'retorno_individual': float(pelicula['return']),
                    'costo': pelicula['budget'],
                    'ganancia': pelicula['revenue']
                }
                peliculas_info.append(info_pelicula)

            return {
                'director': nombre_director,
                'retorno_total_director': retorno_total_director,
                'peliculas': peliculas_info
            }
        else:
            return f'No se encontró ninguna película dirigida por "{nombre_director}" en el dataset.'

    def recomendar_peliculas(self, pelicula_entrada: str):

        # Convertir el título de la película de entrada a minúsculas
        pelicula_entrada = pelicula_entrada.lower()

        # Convertir los títulos en el DataFrame a minúsculas
        df_movies_norm['title_lower'] = df_movies_norm['title'].str.lower()

        """
        Recomienda películas similares a una película de entrada.

        Args:
            pelicula_entrada (str): El título de la película de entrada.
            df_movies_norm (pd.DataFrame): El DataFrame con la información de las películas.

        Returns:
            dict: Un diccionario con las recomendaciones de películas.

        """
        # Filtrar el DataFrame df_movies_norm por la película de entrada
        filtrado = df_movies_norm[df_movies_norm['title'] == pelicula_entrada]

        # Verificar si se encontró la película de entrada
        if len(filtrado) > 0:
            pelicula_entrada = filtrado.iloc[0]

            # Obtener los géneros de la película de entrada
            generos_entrada = pelicula_entrada['genres'].split('|')

            # Filtrar el DataFrame df_movies_norm por los géneros de la película de entrada
            filtrado_generos = df_movies_norm[df_movies_norm['genres'].apply(lambda x: any(genero in x for genero in generos_entrada))]

            # Excluir la película de entrada del DataFrame filtrado_generos
            filtrado_generos = filtrado_generos[filtrado_generos['title'] != pelicula_entrada['title']]

            # Ordenar las películas por el score y la popularidad en orden descendente
            recomendaciones = filtrado_generos.sort_values(by=['score', 'popularity'], ascending=False)

            # Seleccionar las 5 primeras películas como recomendaciones
            recomendaciones = recomendaciones.head(5)

            # Crear una lista para almacenar la información de cada película recomendada
            peliculas_recomendadas = []

            # Recorrer cada película recomendada
            for index, pelicula in recomendaciones.iterrows():
                info_pelicula = {
                    'titulo': pelicula['title'],
                    'fecha_lanzamiento': pelicula['release_date'].strftime('%Y-%m-%d'),
                    'score': pelicula['score'],
                    'popularidad': pelicula['popularity']
                }
                peliculas_recomendadas.append(info_pelicula)

            return {
                'pelicula_entrada': pelicula_entrada['title'],
                'recomendaciones': peliculas_recomendadas
            }
        else:
            return f'No se encontró ninguna película con título "{pelicula_entrada}" en el dataset.'
        
# Exportar CVS a DataFrames, entorno local

path_in_movies = 'Data Set/df_movies_norm.csv'
path_in_credits = 'Data Set/df_credits_norm.csv'

df_movies_norm = pd.read_csv(path_in_movies, encoding='UTF-8', decimal='.')
df_credits_norm = pd.read_csv(path_in_credits,encoding='UTF-8')
# Convertir la columna 'release_date' a tipo datetime
df_movies_norm['release_date'] = pd.to_datetime(df_movies_norm['release_date'])
def replace_null_values(data):
    """
    Reemplaza los valores nulos en las columnas de tipo objeto con una cadena vacía ('') y los valores nulos
    en las columnas de tipo float con 0.
    """
    object_columns = data.select_dtypes(include='object').columns
    float_columns = data.select_dtypes(include=['float64', 'float32']).columns
    data[object_columns] = data[object_columns].fillna('')
    data[float_columns] = data[float_columns].fillna(0)
replace_null_values(df_movies_norm)

# Instanciar la clase MovieAnalyzer
movie_analyzer = MovieAnalyzer()

# Crear una instancia de FastAPI
app = FastAPI()

# Definir las rutas de la API
@app.get("/")
def read_root():
    return {"API": "Análisis de películas"}

@app.get("/healthz", status_code=200)
async def health_check():
    return {"status": "OK"}

@app.get("/filmaciones/mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    return movie_analyzer.cantidad_filmaciones_mes(mes)

@app.get("/filmaciones/dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    return movie_analyzer.cantidad_filmaciones_dia(dia)

@app.get("/peliculas/score/{titulo}")
def score_titulo(titulo: str):
    return movie_analyzer.score_titulo(titulo)

@app.get("/peliculas/votos/{titulo}")
def votos_titulo(titulo: str):
    return movie_analyzer.votos_titulo(titulo)

@app.get("/actores/{nombre_actor}")
def get_actor(nombre_actor: str):
    return movie_analyzer.get_actor(nombre_actor)

@app.get("/directores/{nombre_director}")
def get_director(nombre_director: str):
    return movie_analyzer.get_director(nombre_director)

@app.get("/recomendar/{pelicula_entrada}")
def recomendar_peliculas(pelicula_entrada: str):
    return movie_analyzer.recomendar_peliculas(pelicula_entrada, df_movies_norm)