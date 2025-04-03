from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

class QueryParser:
    def __init__(self, model_name="llama3.2"):
        self.llm = Ollama(model=model_name)

        self.prompt = PromptTemplate.from_template("""
            You are an AI that converts user questions, in Spanish, into secure SQL queries.

            - The database has the following tables:
              1. `Retail Clients` (Customer ID,	Customer, Name,	Email, Phone, City, State,	Country,	Age,	Gender)
              2. `Retail Products` (Product ID,	Product Name,	Category,	Sub-Category,	Product_Brand)
              3. `Retail Sales` (Order ID,	Order Date,	Customer ID,	Product ID,	Sales,	Quantity,	Total_Amount)

            - Rules for SQL generation:
              1. **Only SELECT queries** (No DELETE, UPDATE, or INSERT).
              2. **Use LIMIT 10 for large queries**.
              3. **Avoid using wildcards (`SELECT *`)**.
              4. **Prevent SQL injection by parameterizing values**.
              5. **Join tables only if necessary**.

            - Examples:
              User: "Muestrame los 5 productos más vendidos."
              SQL: "SELECT product_name, SUM(quantity) AS total_sold FROM sales GROUP BY product_name ORDER BY total_sold DESC LIMIT 5;"

              User: "¿Cuántas ventas fueron hechas en los últimos 7 días?"
              SQL: "SELECT COUNT(*) FROM sales WHERE date >= CURDATE() - INTERVAL 7 DAY;"

              User: "{query}"
              SQL:
        """)

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate_sql(self, user_query):
        sql_query = self.chain.invoke({"query": user_query})
        return sql_query.strip()
