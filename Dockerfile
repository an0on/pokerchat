# Dockerfile

# Basis-Image (wähle eine passende Python-Version)
FROM python:3.10-slim

# Setze Umgebungsvariablen für Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Installiere Systemabhängigkeiten falls nötig (hier nicht, aber als Beispiel)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Kopiere die Abhängigkeitsdatei zuerst, um Docker Layer Caching zu nutzen
COPY requirements.txt .

# Installiere Python-Abhängigkeiten
# --no-cache-dir reduziert die Image-Größe
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Anwendungscodes in das Arbeitsverzeichnis
# Dies schließt app.py, templates/, static/ etc. ein
COPY . .

# Setze Umgebungsvariablen für Flask/Gunicorn
# PORT wird oft von der Hosting-Plattform (wie Coolify) überschrieben
ENV PORT=8787
# FLASK_APP wird von Gunicorn verwendet, um die App zu finden
ENV FLASK_APP=app:app

# Exponiere den Port, auf dem Gunicorn laufen wird (muss mit ENV PORT übereinstimmen)
EXPOSE 8787

# Kommando zum Starten der Anwendung mit Gunicorn (Produktionsserver)
# Läuft auf Port 5000 und ist von außerhalb des Containers erreichbar (0.0.0.0)
# 'app:app' bedeutet: In der Datei 'app.py' finde die Flask-Instanz namens 'app'
# Passe die Anzahl der Worker (-w) und Threads nach Bedarf an
CMD ["gunicorn", "--bind", "0.0.0.0:8787", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
