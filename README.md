# turismo_espana
Conjunto de notebooks de Jupyter y rutinas de Python para conectarse con la API de dataestur y guardar estos datos en una coleccion de MongoDB.

La version final que actualiza la base de datos diariamente (Con las predicciones) esta en el archivo Python **FINAL_actualizacion_predicciones**

Adicionalmente se incluyen:
- Los 9 notebooks utilizados para la exploracion de datos y algoritmos.
- Los modelos exportados en archivos .pkl para cada comunidad.
- Los 2 tipos de scripts bash (.sh) usados para ejecutar el script Python desde cron automaticamente (Cada 6 horas). En el segundo archivo se incluye la carga de un archivo .env ya que cron no carga por defecto variables de entorno.
