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
            1. `clients` ('customer_id', 'customer_name', 'city', 'state', 'country', 'company_id', 'email', 'phone', 'age', 'gender')
            2. `products` ('product_id', 'product_name', 'category', 'subcategory', 'company_id', 'product_brand')
            3. `sales` ('order_id', 'order_date', 'customer_id', 'product_id', 'sales', 'quantity', 'profit', 'company_id', 'total_amount')

            Ejemplos:
            User: "Muestrame el top 5 de productos mas vendidos."
            SQL: "SELECT p.product_name, SUM(s.total_amount) AS total_sales FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.product_name ORDER BY Total_Sales DESC LIMIT 5;"

            User: "Cuantas ventas fueron realizadas en los ultimos 7 dias?"
            SQL: "SELECT COUNT(*) FROM sales WHERE order_date >= CURDATE() - INTERVAL 7 DAY;"

            User:"¿Cuáles son los 10 clientes con más compras en la compañía 2?"
            SQL: SELECT c.customer_id, c.customer_name, SUM(s.quantity) AS total_items_purchased FROM sales s JOIN clients c ON s.customer_id = c.customer_id AND s.company_id = c.company_id WHERE s.company_id = 2 GROUP BY c.customer_id, c.customer_name ORDER BY total_items_purchased DESC LIMIT 10;

            Pregunta: {query}
            SQL:
        """)

    def generate_sql(self, user_query: str) -> str:
        try:
            if not isinstance(user_query, str):
                raise TypeError("User query must be a string.")

            formatted_prompt = self.prompt.format(query=user_query)
            sql_query = self.llm.invoke(formatted_prompt)

            return sql_query.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""