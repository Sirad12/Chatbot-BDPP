import json
import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY manquante — vérifiez votre fichier .env")

genai.configure(api_key=GOOGLE_API_KEY)

#Transforme le texte en vecteur 
EMBEDDING_MODEL = "models/gemini-embedding-001"

#La fonction embed_text(text: str) -> list[float] qui utilise genai.embed_content(...)
def embed_text(text:str) -> list[float]:
    result = genai.embed_content(
        model= EMBEDDING_MODEL,
        content= text,
        task_type= "retrieval_document"
    )
    return result["embedding"]


COLLECTION_NAME = "passeport_senegal"
#La fonction main() qui lit le fichier JSON, crée une collection ChromaDB et insère les embeddings
def main():
    #Lecture
    with open("data/knowledge_base.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    #Cette ligne crée (ou ouvre, si elle existe déjà) une base de données vectorielle ChromaDB stockée sur le disque, dans le dossier
    client = chromadb.PersistentClient(path="./chromadb")
    print(f"{len(chunks)} chunks chargés")

    #Collection
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception: 
        pass 
    collection = client.create_collection(COLLECTION_NAME)

    #Les embeddings
    ids, embeddings,documents = [], [], []

    for chunk in chunks:
        vector = embed_text(chunk["text"])
        ids.append(chunk["id"])
        embeddings.append(vector)
        documents.append(chunk["text"])
        print(f" {chunk['id']} traité !")

    collection.add(embeddings=embeddings, ids=ids, documents=documents)

if __name__ == "__main__":
    main()










