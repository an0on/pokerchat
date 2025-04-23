# app.py
import os
import requests
import json
# NEU: render_template hinzufügen
from flask import Flask, request, jsonify, render_template, send_from_directory
from supabase import create_client, Client
from dotenv import load_dotenv

# Lade Umgebungsvariablen für lokale Entwicklung (optional)
load_dotenv()

# --- Konfiguration ---
# (Supabase und Ollama Konfigurationen bleiben gleich)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_TABLE_NAME = os.environ.get("SUPABASE_TABLE_NAME", "regelwerk_chunks")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

# Initialisierung
# NEU: static_folder und template_folder explizit definieren (oft Standard, aber sicher ist sicher)
app = Flask(__name__, template_folder='templates', static_folder='static')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Hilfsfunktionen ---
# (get_chunks_from_supabase und query_ollama bleiben unverändert)
def get_chunks_from_supabase(query: str = None, limit: int = 5) -> list:
    # ... (Code von vorheriger Antwort)
    try:
        response = supabase.table(SUPABASE_TABLE_NAME).select("content").limit(limit).execute() # Annahme: Spalte heißt 'content'
        if response.data:
            return [item['content'] for item in response.data]
        else:
            app.logger.warning(f"Keine Daten aus Supabase Tabelle '{SUPABASE_TABLE_NAME}' erhalten.")
            return []
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen von Chunks aus Supabase: {e}")
        return []

def query_ollama(prompt: str) -> str:
    # ... (Code von vorheriger Antwort)
    ollama_api_url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(ollama_api_url, headers=headers, data=json.dumps(payload), timeout=120)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler bei der Kommunikation mit Ollama unter {ollama_api_url}: {e}")
        return f"Fehler bei der Kommunikation mit Ollama: {e}"
    except Exception as e:
        app.logger.error(f"Unerwarteter Fehler beim Abfragen von Ollama: {e}")
        return f"Unerwarteter Fehler beim Abfragen von Ollama: {e}"

# --- NEU: Route zum Ausliefern der HTML-Seite ---
@app.route('/')
def home():
    """Liefert die Haupt-Chat-Seite aus."""
    return render_template('index.html')

# --- API Endpunkt (bleibt gleich) ---
def process_query():
    """
    Nimmt eine Anfrage vom Frontend entgegen, holt Chunks, fragt Mistral
    und gibt die Antwort als JSON zurück.
    Erwartet JSON im Body: { "query": "Deine Frage oder dein Text hier" }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "Missing 'query' in JSON body"}), 400

    app.logger.info(f"API-Anfrage erhalten: {user_query}")

    # 1. Chunks holen (optional, anpassen)
    retrieved_chunks = get_chunks_from_supabase(query=user_query, limit=3)

    # 2. Prompt erstellen (anpassen)
    context = "\n\n".join(retrieved_chunks)
    prompt = f"""Basierend auf dem folgenden Kontext:
--- Kontext Anfang ---
{context if retrieved_chunks else 'Kein spezifischer Kontext gefunden.'}
--- Kontext Ende ---

Beantworte die folgende Frage oder reagiere auf die Aussage: {user_query}"""
    if not retrieved_chunks:
        prompt = user_query # Fallback ohne Kontext

    app.logger.info(f"Sende Prompt an Ollama ({OLLAMA_MODEL})...")

    # 3. Ollama/Mistral abfragen
    mistral_response = query_ollama(prompt)

    # 4. Antwort zurückgeben (als JSON für das Frontend)
    return jsonify({
        "query": user_query, # Optional die ursprüngliche Query zurückgeben
        "response": mistral_response
    })

# --- Startpunkt für lokale Entwicklung ---
if __name__ == '__main__':
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Fehler: SUPABASE_URL und SUPABASE_KEY müssen gesetzt sein.")
    else:
        app.run(debug=True, host='0.0.0.0', port=8787)
