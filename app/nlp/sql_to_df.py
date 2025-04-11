from flask import Flask, request, jsonify
import pandas as pd
from nlp.query_parser import QueryParser
from database.db_connector import get_db_connection
from nlp.sql_validator import validate_sql

app = Flask(__name__)
parser = QueryParser()

@app.route('/query', methods=['POST'])
def query_database():
    """
    Endpoint para recibir una pregunta en lenguaje natural y devolver
    los resultados de la consulta SQL generada.
    """
    data = request.get_json()
    if not data or 'pregunta' not in data:
        return jsonify({"error": "Se requiere el campo 'pregunta' en el JSON."}), 400

    pregunta = data['pregunta']
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos. Revisa la configuración."}), 500

    try:
        sql = parser.generate_sql(pregunta)

        # Validar la consulta SQL antes de ejecutarla
        is_valid, validation_message = validate_sql(sql)
        if not is_valid:
            return jsonify({"error": f"Consulta SQL inválida: {validation_message}"}), 400

        df_resultado = pd.read_sql(sql, conn)
        conn.close()
        # Convertir el DataFrame a una lista de diccionarios para JSON
        resultados_json = df_resultado.head(10).to_dict(orient='records')
        return jsonify({"resultado": resultados_json}), 200

    except Exception as e:
        if conn and conn.is_connected():
            conn.close()
        return jsonify({"error": f"Error al ejecutar la consulta: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True) # No usar debug=True en producción
