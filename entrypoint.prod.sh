#!/bin/bash

echo "🚧 Starte Migrationen..."
python manage.py migrate

echo "🎨 Sammle statische Dateien..."
python manage.py collectstatic --noinput

echo "👤 Erstelle Superuser (wenn nicht vorhanden)..."
python manage.py createsuperuser \
  --noinput \
  --username "$DJANGO_SUPERUSER_USERNAME" \
  --email "$DJANGO_SUPERUSER_EMAIL" || true

echo "🚀 Starte Gunicorn..."
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --access-logfile - \
  --error-logfile - \
  videoflix.wsgi:application
