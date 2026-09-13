#!/bin/sh
# Prepares the container before the main command (Gunicorn) starts.
set -e

# Create a random secret key on the first start, unless DJANGO_SECRET_KEY is set (.env).
# The key is stored in the data volume, so it survives restarts and rebuilds.
if [ -z "$DJANGO_SECRET_KEY" ] && [ ! -s data/secret_key ]; then
    (umask 077 && python -c "import secrets; print(secrets.token_urlsafe(50))" > data/secret_key)
    echo "Created a new secret key in data/secret_key"
fi

# Apply database migrations (creates the SQLite database on the first start)
python manage.py migrate --noinput

# Copy all static files to STATIC_ROOT (volume shared with Nginx)
python manage.py collectstatic --noinput

# Replace the shell with the main command, so Gunicorn runs as PID 1 and receives stop signals
exec "$@"
