FROM python:3.13-slim

# No .pyc files, unbuffered output (logs show up immediately in 'docker compose logs')
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run as an unprivileged user. data/ (SQLite) and staticfiles/ (shared with Nginx)
# become volumes, so the user needs write access to both directories.
RUN groupadd --system django \
    && useradd --system --gid django --no-create-home django \
    && mkdir -p /app/data /app/staticfiles \
    && chown django:django /app/data /app/staticfiles \
    && chmod +x /app/entrypoint.sh
USER django

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "app.wsgi:application"]
