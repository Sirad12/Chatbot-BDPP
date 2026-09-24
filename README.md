# Chatbot RAG — Bureau des Passeports du Sénégal

Chatbot conversationnel basé sur une architecture **RAG (Retrieval-Augmented
Generation)**, répondant aux questions administratives sur les démarches de
passeport au Sénégal (documents requis, tarifs, délais, renouvellement,
perte/vol, etc.).

## Pourquoi ce cas d'usage ?

Les démarches de passeport génèrent de nombreuses questions récurrentes de
la part des citoyens (documents à fournir, délais, prise de rendez-vous),
souvent posées sur les réseaux sociaux faute de réponse rapide et
centralisée. Un chatbot RAG permet de répondre instantanément à partir
d'une base de connaissances fiable, sans surcharger les commissariats de
demandes d'information simples.

## Architecture
Question utilisateur
│
▼
POST /chat (FastAPI)
│
▼

Embedding de la question — Gemini text-embedding-001
│
▼
Retrieval — recherche des chunks les plus proches (ChromaDB, ./chromadb)
│
▼
Génération — Gemini 3.5 Flash-lite répond à partir du contexte récupéré
│
▼
Réponse JSON { "reponse": "..." }



- **Données** : documents rassemblés à partir des informations officielles
  du Ministère de l'Intérieur et de la DGSE (documents requis, tarifs,
  délais, procédures)
- **Chunking** : découpage manuel par thématique — un chunk = une
  information autonome
- **Retriever** : ChromaDB (base vectorielle locale, persistante dans
  `./chromadb`)
- **Modèle d'embedding** : `text-embedding-001` (Google)
- **Génération** : `gemini-3.5-flash-lite` (Google AI Studio), appelé en
  transport REST (`transport="rest"`) pour éviter les blocages réseau liés
  au protocole gRPC

## Lancer le projet en local

```bash
pip install -r requirements.txt
cp .env.example .env          # puis coller votre clé API Gemini
python ingest.py              # vectorise et indexe la base de connaissances
python main.py                # démarre l'API sur http://localhost:8500
```

## Tester l'API

Documentation interactive : `http://localhost:8500/docs`

Ou en ligne de commande :

```bash
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels documents pour une première demande de passeport ?"}'
```

Réponse attendue (exemple) :
```json
{
  "reponse": "Voici les documents requis pour une première demande de passeport, selon la situation du demandeur : Pour un majeur : la carte nationale d'identité (CNI) originale en cours de validité ; une copie certifiée conforme de la CNI ; un certificat de nationalité ou un ancien passeport ; une quittance attestant du paiement des frais. Pour un enfant mineur : une autorisation parentale ; la copie certifiée conforme de la carte nationale d'identité du père ou de la mère ; un certificat de prise en charge délivré par la mairie ou la justice..."
}
```

## Lancer avec Docker

```bash
docker login
docker build -t votre_pseudo/chatbot-rag .
docker run -p 8500:8500 -e GOOGLE_API_KEY=votre_cle_gemini votre_pseudo/chatbot-rag
```

## Structure du projet
Chatbot-BDPP/
├── data/ # base de connaissances (chunks)
├── chromadb/ # base vectorielle persistante (générée par ingest.py)
├── ingest.py # vectorisation + indexation ChromaDB
├── test_retrieval.py
├── main.py # API FastAPI (route /chat)
├── requirements.txt
├── Dockerfile
├── .env
├── .gitignore
└── README.md

---
*Réalisée par Ndeye Sira Dia — Etudiante en Licence 3 Big Data & IA*