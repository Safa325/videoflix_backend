# Stage 1: Builder
FROM python:3.11 AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11

# Install ffmpeg + set PATH
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
ENV PATH="/usr/bin:${PATH}"

# Benutzer + Verzeichnis
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Python-Pakete aus Stage 1 kopieren
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# App-Code kopieren
WORKDIR /app
COPY --chown=appuser:appuser . /app/
COPY --chown=appuser:appuser entrypoint.prod.sh /app/entrypoint.prod.sh
RUN chmod +x /app/entrypoint.prod.sh

# Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000
CMD ["/app/entrypoint.prod.sh"]