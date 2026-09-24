import os

import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

EMBEDDING_MODEL = "models/gemini-embedding-001"
COLLECTION_NAME = "passeport_senegal"

client = chromadb.PersistentClient(path="./chromadb")
collection = client.get_collection(COLLECTION_NAME)

print(collection.count())

question = "combien coûte le renouvellement ?"

result = genai.embed_content(
    model=EMBEDDING_MODEL,
    content=question,
    task_type="retrieval_query",
)
question_vector = result["embedding"]

resultats = collection.query(
    query_embeddings=[question_vector],
    n_results=3, #les trois chunks les plus proches
)

print(resultats)