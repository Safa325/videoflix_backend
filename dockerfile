FROM python:3.12.3

# Arbeitsverzeichnis setzen
WORKDIR /app

# Systempakete & Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Projektdateien kopieren
COPY . .

# Entrypoint setzen & ausführbar machen
COPY entrypoint.prod.sh /app/entrypoint.prod.sh
RUN chmod +x /app/entrypoint.prod.sh

# Port freigeben
EXPOSE 8000

# Container-Start
CMD ["/app/entrypoint.prod.sh"]
