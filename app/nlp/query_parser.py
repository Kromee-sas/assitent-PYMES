from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
import re

class QueryParser:
    def __init__(self, model_name: str = "llama3.2"):
        self.llm = OllamaLLM(model=model_name)

        self.prompt = PromptTemplate.from_template("""
            Convierte la siguiente pregunta en español en una consulta SQL segura.

            Reglas:
            - SOLO devuelve la consulta, sin explicaciones.
            - Usa LIMIT 10 si no se especifica un límite.
            - Evita SELECT *, usa columnas explícitas.
            - Usa nombres de tabla exactos.

            Tablas disponibles:
            1. `clients` ('customer_id', 'customer_name', 'city', 'state', 'country', 'company_id', 'email', 'phone', 'age', 'gender')
            2. `products` ('product_id', 'product_name', 'category', 'subcategory', 'company_id', 'product_brand')
            3. `sales` ('order_id', 'order_date', 'customer_id', 'product_id', 'sales', 'quantity', 'profit', 'company_id', 'total_amount')

            Ejemplos:
            User: "¿Cuáles son los productos más vendidos?"
            SQL: SELECT p.product_name, SUM(s.total_amount) AS total_sales FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.product_name ORDER BY total_sales DESC LIMIT 10;

            User: "¿Cuántas ventas se realizaron la semana pasada?"
            SQL: SELECT COUNT(*) FROM sales WHERE order_date >= CURDATE() - INTERVAL 7 DAY;

            Pregunta: {query}
            SQL:
        """)

    def generate_sql(self, user_query: str, company_id: int = None) -> str:
        try:
            if not isinstance(user_query, str):
                raise TypeError("Query must be a string.")

            formatted_prompt = self.prompt.format(query=user_query)
            sql_query = self.llm.invoke(formatted_prompt).strip()

            if company_id is not None:
                sql_query = self._inject_company_filter(sql_query, company_id)

            return sql_query

        except Exception as e:
            print(f"[QueryParser] Error: {e}")
            return ""

    def _inject_company_filter(self, sql_query: str, company_id: int) -> str:
        # Check if company_id already exists
        if re.search(r"company_id\s*=\s*\d+", sql_query, re.IGNORECASE):
            return sql_query

        # Simple WHERE or AND injection
        if "WHERE" in sql_query.upper():
            return re.sub(r"(WHERE)", f"\\1 company_id = {company_id} AND", sql_query, flags=re.IGNORECASE)
        elif "GROUP BY" in sql_query.upper():
            return sql_query.replace("GROUP BY", f"WHERE company_id = {company_id} GROUP BY")
        elif "ORDER BY" in sql_query.upper():
            return sql_query.replace("ORDER BY", f"WHERE company_id = {company_id} ORDER BY")
        elif ";" in sql_query:
            return sql_query.replace(";", f" WHERE company_id = {company_id};")
        else:
            return sql_query + f" WHERE company_id = {company_id}"