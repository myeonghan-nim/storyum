#!/usr/bin/env sh
set -e

: "${DJANGO_SETTINGS_MODULE:=storyum.settings}"

echo ">>> Migration"
python manage.py migrate --noinput

echo ">>> Collect static files"
python manage.py collectstatic --noinput

echo ">>> Starting server"
exec gunicorn storyum.wsgi:application --config ./gunicorn.py
