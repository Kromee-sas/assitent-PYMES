from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM

class QueryParser:
    def __init__(self, model_name: str = "llama3.2"):
        self.llm = OllamaLLM(model=model_name)

        self.prompt = PromptTemplate.from_template("""
            Convierte la siguiente pregunta en español en una consulta segura.

            Reglas:
            - SOLO devuelve la consulta, sin explicaciones ni comentarios.
            - Usa `LIMIT 10` en consultas grandes.
            - Evita `SELECT *`, usa nombres de columnas específicos.
            - Usa nombres de tabla exactos.

            Tablas disponibles:
            1. `Clients_2` (Customer_ID, Customer_Name, Email, Phone, City, State, Country, Age, Gender)
            2. `Products_2` (Product_ID, Product_Name, Category, Sub_Category, Product_Brand)
            3. `Sales_2` (Order_ID, Order_Date, Customer_ID, Product_ID, Sales, Quantity, Total_Amount)

            Pregunta: {query}
            SQL:
        """)

    def generate_sql(self, user_query: str) -> str:
        try:
            if not isinstance(user_query, str):
                raise TypeError("User query must be a string.")

            formatted_prompt = self.prompt.format(query=user_query)
            sql_query = self.llm.invoke(formatted_prompt)

            print(f"Generated query: {sql_query.strip()}")
            return sql_query.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
