FROM python:3.12.3

# Systempakete installieren (inkl. ffmpeg)
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Python requirements installieren
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Projektcode kopieren
COPY . .

# Entrypoint Script setzen
COPY entrypoint.prod.sh /app/entrypoint.prod.sh
RUN chmod +x /app/entrypoint.prod.sh

# Port freigeben
EXPOSE 8000

# Start des Containers
CMD ["/app/entrypoint.prod.sh"]
