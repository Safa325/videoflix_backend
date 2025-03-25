# Stage 1: Builder stage (install dependencies)
FROM python:3.11 AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11

# 🔧 ffmpeg installieren
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Benutzer + Verzeichnis
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

COPY --chown=appuser:appuser entrypoint.prod.sh /app/
RUN chmod 755 /app/entrypoint.prod.sh
RUN chmod +x /app/entrypoint.prod.sh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["/app/entrypoint.prod.sh"]
