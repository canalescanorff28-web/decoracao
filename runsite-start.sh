#!/usr/bin/env sh
set -eu
python manage.py migrate --noinput
python manage.py seed_catalog
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8080}" --workers "${WEB_CONCURRENCY:-1}" --timeout 60 --access-logfile - --error-logfile -
