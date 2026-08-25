#!/usr/bin/env sh
set -eu

echo "==> Verificando configuração Django..."
python manage.py check --deploy --fail-level ERROR

echo "==> Aplicando migrations..."
python manage.py migrate --noinput

echo "==> Garantindo configurações e catálogo inicial..."
python manage.py seed_catalog

echo "==> Iniciando Gunicorn em 0.0.0.0:${PORT:-8080}..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8080}" \
  --workers "${WEB_CONCURRENCY:-1}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
