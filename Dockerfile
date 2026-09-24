FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8500

CMD ["sh", "-c", "rm -rf /app/chroma_db && python ingest.py && uvicorn main:app --host 0.0.0.0 --port 8500"]