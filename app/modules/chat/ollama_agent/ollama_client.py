# app/modules/chat/nlp/ollama_client.py

from dotenv import load_dotenv
import os
from langchain_community.utilities import SQLDatabase
from langchain_ollama.llms import OllamaLLM
from typing import Any
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda, RunnableWithFallbacks
from langgraph.prebuilt import ToolNode
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import AIMessage

# Cargar variables de entorno
load_dotenv()

# Inicializar la base de datos SQL
engine = os.getenv("DATABASE_URL")
db = SQLDatabase.from_uri(engine)

# Inicializar el modelo de lenguaje de Ollama
llm = OllamaLLM(model='llama3.2')

# Funciones de Utilidad

def create_tool_node_with_fallback(tools: list) -> RunnableWithFallbacks[Any, dict]:
    """
    Create a ToolNode with a fallback to handle errors and surface them to the agent.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

# Crear las herramientas necesarias para el agente
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

def db_query_tool(query: str) -> str:
    result = db.run_no_throw(query)
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    return result

# Definir el estado para el agente
class State(TypedDict):
    message: Annotated[list[AnyMessage], add_messages]

# Definir el nuevo grafo
workflow = StateGraph(State)

# nodos de flujo
def first_tool_call(state: State) -> dict[str, list[AIMessage]]:
    return{
        message: [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "sql_db_list_tables",
                        "args": {},
                        "id": "tool_001"
                    }
                ]
            )
        ]
    }

def model_check_query(state: State) -> dict[str, list[AIMessage]]:
    return {"messages": [query_check.invoke({"message": [state["message"][-1]]})]}

workflow.add_node("first_tool_call", first_tool_call)

workflow.add_node(
    "list_tables_tool", create_tool_node_with_fallback([list_tables_tool])
)
workflow.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))

model_get_schema = llm.bind_tools(
    [get_schema_tool]
)
workflow.add_node(
    "model_get_schema",
    lambda state: {
        "messages": [model_get_schema.invoke(state["messages"])],
    },
)

class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(..., description="La respuesta final para el usruario.")

query_gen_system = """Eres un experto en SQL con gran atención al detalle.

Dada una pregunta de entrada, genera una consulta MySQL sintácticamente correcta para ejecutarla y, luego de revisar los resultados, devuelve la respuesta final.
NO debes usar ninguna herramienta excepto `SubmitFinalAnswer` para enviar la respuesta final al usuario.
Al generar la consulta SQL:

- Escribe directamente la consulta SQL que responde a la pregunta, sin usar ninguna herramienta adicional.

- A menos que el usuario indique explícitamente cuántos ejemplos desea obtener, limita siempre la consulta a un máximo de 5 resultados.

- Puedes ordenar los resultados por una columna relevante para mostrar los ejemplos más interesantes en la base de datos.

- Nunca consultes todas las columnas de una tabla. Solicita solo las columnas necesarias según la pregunta.

- Si se produce un error al ejecutar la consulta, reescríbela y vuelve a intentarlo.

- Si el resultado de la consulta está vacío, intenta reescribirla para obtener un conjunto de resultados no vacío.

- Nunca inventes información si no tienes suficientes datos para responder. Simplemente indica que no hay suficiente información.

- Si tienes suficiente información para responder la pregunta, invoca la herramienta adecuada (SubmitFinalAnswer) para entregar la respuesta final al usuario.

NO hagas ninguna instrucción DML (como INSERT, UPDATE, DELETE, DROP, etc.) en la base de datos."""

query_gen_prompt = ChatPromptTemplate.from_messages(
    [("system", query_gen_system), ("placeholder", "{messages}")]
)
query_gen = query_gen_prompt | llm.bind_tools(
    [SubmitFinalAnswer]
)

def query_gen_node(state: State):
    message = query_gen.invoke(state)

    tool_messages = []
    if message.tool_calls:
        for tc in message.tool_calls:
            if tc["name"] != "SubmitFinalAnswer":
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: The wrong tool was called: {tc['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
                        tool_call_id=tc["id"],
                    )
                )
    else:
        tool_messages = []
    return {"messages": [message] + tool_messages}

workflow.add_node("query_gen", query_gen_node)

workflow.add_node("correct_query", model_check_query)

workflow.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))

# Control de flujo
def should_continue(state: State) -> Literal[END, "correct_query", "query_gen"]:
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return END
    if last_message.content.startswith("Error:"):
        return "query_gen"
    else:
        return "correct_query"


# Definir los nodos
workflow.add_edge(START, "first_tool_call")
workflow.add_edge("first_tool_call", "list_tables_tool")
workflow.add_edge("list_tables_tool", "model_get_schema")
workflow.add_edge("model_get_schema", "get_schema_tool")
workflow.add_edge("get_schema_tool", "query_gen")
workflow.add_conditional_edges(
    "query_gen",
    should_continue,
)
workflow.add_edge("correct_query", "execute_query")
workflow.add_edge("execute_query", "query_gen")

# Compile the workflow into a runnable
app = workflow.compile()