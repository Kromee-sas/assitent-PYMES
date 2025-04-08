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
            2. `Products_2` (Product_ID, Product_Name, Category, Subcategory, Product_Brand)
            3. `Sales_2` (Order_ID, Order_Date, Customer_ID, Product_ID, Sales, Quantity, Total_Amount)

            Ejemplos:
            User: "Muestrame el top 5 de productos mas vendidos."
            SQL: "SELECT p.Product_Name, SUM(s.Total_Amount) AS Total_Sales FROM Sales_2 s JOIN Products_2 p ON s.Product_ID = p.Product_ID GROUP BY p.Product_Name ORDER BY Total_Sales DESC LIMIT 5;"

            User: "Cuantas ventas fueron realizadas en los ultimos 7 dias?"
            SQL: "SELECT COUNT(*) FROM sales WHERE date >= CURDATE() - INTERVAL 7 DAY;"

            Pregunta: {query}
            SQL:
        """)

    def generate_sql(self, user_query: str) -> str:
        try:
            if not isinstance(user_query, str):
                raise TypeError("User query must be a string.")

            formatted_prompt = self.prompt.format(query=user_query)
            sql_query = self.llm.invoke(formatted_prompt)

            return "Genetated query: " + sql_query.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""