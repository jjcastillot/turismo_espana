from pymongo import MongoClient
import logging
import os
import pandas as pd
import joblib
from itertools import product
import matplotlib.pyplot as plt
import numpy as np
import requests
from io import BytesIO

# Configuracion basica
mongo_user = os.environ.get("MONGO_USER")
mongo_password = os.environ.get("MONGO_PASSWORD")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s', handlers=[logging.StreamHandler()])

# Etapa 1: Solicitud API y actualizacion de DB en MongoDB
# URL base del endpoint
url = "https://dataestur.azure-api.net/API-SEGITTUR-v1/FRONTUR_DL"

# Parámetros de la consulta
params = {
    "desde (año)": 2016,
    "hasta (año)": 2024,
    "País de residencia": "Todos",
    "Tipo de visitante": "Todos",
    "CCAA de destino": "Todos"
}

# Encabezados (para asegurar que aceptamos el formato Excel)
headers = {
    "accept": "application/vnd.ms-excel"
}

# Realizar la solicitud GET
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200 and response.headers['Content-Type'] == 'application/vnd.ms-excel':
    # Leer el archivo Excel desde la respuesta
    excel_file = BytesIO(response.content)
    
    # Leer las hojas disponibles en el archivo
    xls = pd.ExcelFile(excel_file)
    print("Hojas disponibles:", xls.sheet_names)

    # Leer la primera hoja
    df = pd.read_excel(xls, sheet_name=0)
    #logging.info(df.head())
    #Limpieza de espacios en las columnas
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    
    # Conexión a MongoDB 
    client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@localhost:27017/")
    db = client["tfm"]
    collection = db["frontur_dl"]

    # Eliminar la colección si existe (sobrescribir)
    collection.drop()

    # Insertar los datos
    collection.insert_many(df.to_dict("records"))
    logging.info(f"Datos insertados correctamente en MongoDB. Total documentos: {df.shape[0]}")

    # Cerrar conexion
    client.close()
    logging.info("Conexion a MongoDB cerrada correctamente.")

else:
    logging.error(f"Error: No se recibió un archivo Excel válido (status code {response.status_code})")

# Conectarse a MongoDB nuevamente
client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@localhost:27017/")
db = client["tfm"]
collection = db["frontur_dl"]

# Obtener los datos
cursor = collection.find({})
data = list(cursor)

# Convertir a DataFrame
df = pd.DataFrame(data)

# Opcional: eliminar la columna '_id' si no es útil
if "_id" in df.columns:
    df.drop("_id", axis=1, inplace=True)

# Eliminar Ceuta y Melilla
df = df[~df["CCAA_DESTINO"].isin(["Ceuta", "Melilla"])]

# Obtener combinaciones únicas
paises = df['PAIS_RESIDENCIA'].unique()
tipos = df['TIPO_VISITANTE'].unique()
ccaas = df['CCAA_DESTINO'].unique()

# Excluir Ceuta y Melilla
ccaas = [c for c in ccaas if c not in ['Ceuta', 'Melilla']]

# Crear todas las combinaciones posibles para 2025 (12 meses)
combinaciones = list(product(paises, tipos, ccaas, range(1, 13)))

# Construir DataFrame
df_2025 = pd.DataFrame(combinaciones, columns=['PAIS_RESIDENCIA', 'TIPO_VISITANTE', 'CCAA_DESTINO', 'MES'])
df_2025['AÑO'] = 2025

# Reordenar columnas
df_2025 = df_2025[['PAIS_RESIDENCIA', 'TIPO_VISITANTE', 'CCAA_DESTINO', 'AÑO', 'MES']]

# Predecir con cada modelo .pkl correspondiente
predicciones = []

columnas_categoricas = ['PAIS_RESIDENCIA', 'TIPO_VISITANTE']
columnas_numericas = ['AÑO', 'MES']

for comunidad in df_2025['CCAA_DESTINO'].unique():
    # Cargar el modelo de esa comunidad
    modelo_path = f'modelo_{comunidad.replace(" ", "_").lower()}.pkl'
    modelo = joblib.load(modelo_path)

    # Filtrar solo las filas de esa comunidad
    df_comunidad = df_2025[df_2025['CCAA_DESTINO'] == comunidad].copy()
    
    # Preparar features
    X_pred = df_comunidad[columnas_categoricas + columnas_numericas]

    # Hacer predicción
    y_pred = modelo.predict(X_pred)
    # Postprocesamiento: garantizar valores no negativos
    y_pred = np.abs(y_pred)  # Corrige negativos

    # Guardar resultados
    df_comunidad['VISITANTES_PREDICHOS'] = y_pred
    predicciones.append(df_comunidad)

# Unir todas las predicciones
df_resultado_2025 = pd.concat(predicciones, ignore_index=True)

# Guardar resultados en MongoDB

# Conexión a MongoDB 
client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@localhost:27017/")
db = client["tfm"]
collection = db["frontur_dl_2025_pred"]

# Eliminar la colección si existe (sobrescribir)
collection.drop()

# Insertar los datos
collection.insert_many(df_resultado_2025.to_dict("records"))
logging.info(f"Datos predichos 2025 insertados correctamente en MongoDB. Total documentos: {df_resultado_2025.shape[0]}")

# Cerrar conexion
client.close()
logging.info("Conexion a MongoDB cerrada correctamente.")