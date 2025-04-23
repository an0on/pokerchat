import socket

ollama_host = "ollama"  # Ersetze "ollama" durch den tatsächlichen Dienstnamen in Coolify, falls anders
ollama_port = 11434

try:
    # Erstelle ein Socket-Objekt
    sock = socket.create_connection((ollama_host, ollama_port), timeout=5)
    print(f"Verbindung zu {ollama_host}:{ollama_port} erfolgreich!")
    sock.close()
except socket.error as e:
    print(f"Fehler bei der Verbindung zu {ollama_host}:{ollama_port}: {e}")
except socket.timeout:
    print(f"Zeitüberschreitung bei der Verbindung zu {ollama_host}:{ollama_port}")
