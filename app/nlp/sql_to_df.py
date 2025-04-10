# test_query_parser.py
import mysql.connector
import pandas as pd
from query_parser import QueryParser

# Crear instancia del parser
parser = QueryParser()

# Conexión a la base de datos
conn = mysql.connector.connect(
    host="207.244.241.149",
    user="krom_assisten_ia",
    password="envccmvO5%rF9y8K",
    database="krom_assisten_ia"
)

print("Asistente de consultas SQL activado. Escribe 'salir' para terminar.\n")

while True:
    pregunta = input("Pregunta en lenguaje natural:\n")
    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("Saliendo del asistente. ¡Hasta luego!")
        break

    try:
        # Generar la consulta SQL
        sql = parser.generate_sql(pregunta)

        # Ejecutar y mostrar resultados
        df_resultado = pd.read_sql(sql, conn)
        print("Resultado:")
        print(df_resultado.head(10))  # puedes cambiar el número de filas mostradas

    except Exception as e:
        print(f"❌ Error al ejecutar la consulta: {e}")

# Cerrar la conexión al finalizar
conn.close()