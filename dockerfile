# Basis-Image
FROM python:3.11

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere alle Projektdaten
COPY . .

# Setze Umgebungsvariablen
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DJANGO_SETTINGS_MODULE=videoflix.settings

# Sammle statische Dateien
RUN python manage.py collectstatic --noinput

# Exponiere den Port
EXPOSE 8000

# Starte den Gunicorn-Server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "videoflix.wsgi:application"]
