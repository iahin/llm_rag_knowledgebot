from pathlib import Path
import sqlite3
from typing import TypedDict
from langchain_ollama import OllamaLLM
from langchain_ollama import ChatOllama

import pandas as pd
from typing_extensions import Annotated
from Prompt import query_prompt_template
from Typedicts import State
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver



# --- Paths that work regardless of the working directory ---
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "realistic_restaurant_reviews.csv"
DB_NAME = "my_database.db"
DB_DIR = BASE_DIR / DB_NAME

csv_file = CSV_PATH
df = pd.read_csv(csv_file)
conn = sqlite3.connect(DB_DIR)
table_name = "my_table"

df.to_sql(table_name, conn, if_exists="replace", index=False)

db = SQLDatabase.from_uri("sqlite:///"+DB_NAME)

llm = ChatOllama(model="llama3.2", temperature=0)

class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    result = llm.with_structured_output(QueryOutput, method="json_schema").invoke(prompt)
    
    return {"query": result["query"]}


def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f"Question: {state['question']}\n"
        f"SQL Query: {state['query']}\n"
        f"SQL Result: {state['result']}"
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

# output = write_query({"question": "what are 5 reviews that rated 1? without order"})
# print(output)
# q_output = execute_query(output)
# print(q_output)


## Orchestrating with LangGraph
# graph_builder = StateGraph(State).add_sequence(
#     [write_query, execute_query, generate_answer]
# )
# graph_builder.add_edge(START, "write_query")
# graph = graph_builder.compile()

# for step in graph.stream(
#     {"question": "How many unique range of ratings are there? with no limit"}, stream_mode="updates"
# ):
#     print(step)

    
    
## Human in the loop example with MemorySaver
graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory, interrupt_before=["execute_query"])

# Now that we're using persistence, we need to specify a thread ID
# so that we can continue the run after review.
config = {"configurable": {"thread_id": "1"}}

for step in graph.stream(
    {"question": "How many unique range of ratings are there? with no limit"},
    config,
    stream_mode="updates",
):
    print(step)

try:
    user_approval = input("Do you want to go to execute query? (yes/no): ")
except Exception:
    user_approval = "no"

if user_approval.lower() == "yes":
    # If approved, continue the graph execution
    for step in graph.stream(None, config, stream_mode="updates"):
        print(step)
else:
    print("Operation cancelled by user.")
