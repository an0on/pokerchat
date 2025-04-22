from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import requests
import os
import sys
from supabase import create_client, Client

app = FastAPI()

# 💥 Hardcoded (Notfalllösung)
SUPABASE_URL = "https://wplsimkprytlaaxvpjed.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

print("✅ SUPABASE_URL =", SUPABASE_URL)
print("✅ SUPABASE_KEY =", SUPABASE_KEY[:5] + "...")
print("✅ OLLAMA_URL =", OLLAMA_URL)

if not SUPABASE_URL:
    print("❌ ERROR: SUPABASE_URL fehlt!")
    sys.exit(1)

if not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_KEY fehlt!")
    sys.exit(1)

model = SentenceTransformer("all-MiniLM-L6-v2")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class QuestionRequest(BaseModel):
    question: str

def embed_text(text: str):
    return model.encode(text).tolist()

def query_supabase(embedding: list, top_k: int = 3):
    sql = f"""
        SELECT content
        FROM regelwerk_chunks
        ORDER BY embedding <#> '{embedding}'
        LIMIT {top_k};
    """
    result = supabase.rpc("sql", {"query": sql}).execute()
    return [row["content"] for row in result.data] if result.data else []

def query_ollama(prompt: str, model: str = "mistral"):
    res = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": model, "prompt": prompt}
    )
    return res.json().get("response", "") if res.ok else "Fehler bei OLAMA."

@app.post("/ask")
def ask_question(data: QuestionRequest):
    embedding = embed_text(data.question)
    context_chunks = query_supabase(embedding)
    context = "\n---\n".join(context_chunks)
    full_prompt = f"Kontext:\n{context}\n\nFrage: {data.question}\nAntwort:"
    answer = query_ollama(full_prompt)
    return {"answer": answer}
