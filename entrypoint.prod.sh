#!/bin/bash

python manage.py migrate
python manage.py collectstatic --noinput

# Logging aktivieren
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --access-logfile - \
  --error-logfile - \
  videoflix.wsgi:application
