import mysql.connector
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Set up the database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Connect to the database
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        return {"error": f"Error de conexión a la base de datos: {err}"}

# Execute a SQL query and return the results
def execute_query(sql_query):
    try:
        connection = get_db_connection()
        if isinstance(connection, dict):  # Si ocurre un error en la conexión
            return connection
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        return {"error": str(e)}