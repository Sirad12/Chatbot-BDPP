from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn
import os 
import chromadb

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY: 
    raise RuntimeError("GOOGLE_API_KEY manquante — vérifiez votre fichier .env")

#transport="rest" change simplement le protocole réseau utilisé pour parler aux serveurs de Google
genai.configure(api_key=GOOGLE_API_KEY, transport="rest")

EMBEDDING_MODEL = "models/gemini-embedding-001"
COLLECTION_NAME = "passeport_senegal"
CHROMA_PATH = "./chromadb"
GENERATION_MODEL = "gemini-3.5-flash-lite" #Le modele qui va rediger la reponse



#Creation de l'application
app = FastAPI(title="Chatbot RAG - Bureau des Passeports du Sénégal")



client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)

class Question(BaseModel):
    question: str

#On utilise post ici au lieu de get car l'utilisateur doit nous envoyer des donnees (ses questions)
@app.post("/chat")
def chat(payload: Question):
    #Embedding de la question de l'utilisateur 
    result = genai.embed_content(
        model = EMBEDDING_MODEL,
        content = payload.question,
        task_type= "retrieval_query"
    )
    question_vector = result["embedding"]

    #Retrieval : chercher les chunks pertinents dans chromadb
    resultats = collection.query(
        query_embeddings= [question_vector],
        n_results=3,
    )

    #Contruire le prompt avec le contexte trouve
    chunks_trouves = resultats["documents"][0]
    context = "\n\n".join(chunks_trouves)

    SYSTEM_PROMPT =  """Tu es l'assistant virtuel du Bureau des Passeports du Sénégal.
    Tu réponds UNIQUEMENT à partir du contexte fourni ci-dessous, en français,
    de façon claire et concise.

    Règles strictes :
    - Si le contexte ne contient pas l'information demandée, dis clairement
    que tu ne disposes pas de cette information et invite la personne à
    contacter le commissariat ou le consulat compétent.
    - Ne donne jamais d'information que tu n'es pas certain de trouver dans
    le contexte fourni.
    - Reste toujours poli, précis et orienté vers l'aide administrative.

    Contexte :
    {context}
    """
    prompt_final = SYSTEM_PROMPT.format(context=context)

    #Appel du modele de generation et renvoi de la reponse 
    model = genai.GenerativeModel(
        model_name=GENERATION_MODEL,
        system_instruction=prompt_final,
    )
    response = model.generate_content(payload.question)

    return {"reponse": response.text}




if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8500)








