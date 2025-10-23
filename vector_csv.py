from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# --- Paths that work regardless of the working directory ---
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "knowledgebase" / "realistic_restaurant_reviews.csv"
DB_DIR = BASE_DIR / "chroma_langchain_db"

df = pd.read_csv(CSV_PATH)
embeddings = OllamaEmbeddings(model="llama3.2")

db_location = DB_DIR
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []
    for index, row in df.iterrows():
        document = Document(
            page_content=row["Title"] + "\n" +
            row["Review"] + " rating: " + str(row["Rating"]),
            metadata={"rating": row["Rating"], "date": row["Date"]},
            id=str(index)
        )
        ids.append(str(index))
        documents.append(document)

vector_store = Chroma(
    collection_name="pizza_reviews",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)

retriever = vector_store.as_retriever(
    search_type="similarity",  # search algorithm
    search_kwargs={"k": 5}  # number of relevent docs to return
)


# results = retriever.invoke("the taste was bad, experience was bad all was bad rating 1")
# for r in results:
#     print(r)
