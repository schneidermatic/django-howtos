# Gunicorn configuration - loaded automatically from the working directory.
# https://docs.gunicorn.org/en/stable/settings.html
import os

# Listen on all interfaces inside the container. The port is not published,
# only Nginx can reach it via the Compose network.
bind = "0.0.0.0:8000"

# Number of worker processes (rule of thumb: 2 x CPU cores + 1)
workers = int(os.environ.get("GUNICORN_WORKERS", "3"))

# Restart workers that are silent for more than 30 seconds
timeout = 30

# Log requests and errors to stdout/stderr -> 'docker compose logs'
accesslog = "-"
errorlog = "-"
