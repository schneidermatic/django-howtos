HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker
---

This HowTo describes how to run a Django app in a production-like setup with Docker Compose:

- **Gunicorn** runs the Django app instead of the development server.
- **Nginx** terminates HTTPS with a self-signed certificate, redirects HTTP to HTTPS, serves the static files and forwards all other requests to Gunicorn.
- **SQLite** stores the data in a Docker volume, so no database server and no database credentials are needed.

A single `docker compose up` starts everything. On the first start, the app creates its secret key and Nginx creates a self-signed certificate automatically. Both containers are restarted automatically and monitored by health checks.

###### REFERENCES
- [Django documentation - Deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django documentation - How to use Django with Gunicorn](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/gunicorn/)
- [Django documentation - SQLite notes](https://docs.djangoproject.com/en/5.2/ref/databases/#sqlite-notes)
- [Gunicorn documentation - Settings](https://docs.gunicorn.org/en/stable/settings.html)
- [Nginx documentation - Configuring HTTPS servers](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Nginx image on Docker Hub](https://hub.docker.com/_/nginx)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

###### PREREQUISITES
---

Name           | Reference
-------------- | ---------------
Ubuntu         | >= 20.04.6 LTS (Focal Fossa)
Python         | >= v3.10.x (only needed to generate the project skeleton)
Docker Desktop | >= 4.12.0 (with WSL 2 integration enabled)
docker         | [https://docs.docker.com/engine/reference/run/](https://docs.docker.com/engine/reference/run/)
docker-compose | >= v2.24.0 (needed for the optional `.env` file), [https://docs.docker.com/compose/reference/overview/](https://docs.docker.com/compose/reference/overview/)

ARCHITECTURE
---

    Browser --HTTP  :80---> nginx  (301 redirect to HTTPS)
    Browser --HTTPS :443--> nginx --HTTP :8000--> web (Gunicorn + Django)
                              |                     |
                              |                     +-- volume 'sqlite_data': SQLite database + secret key
                              |
                              +-- volume 'nginx_ssl':   self-signed certificate
                              +-- volume 'static_data': static files (written by web, read by nginx)

    Only nginx publishes ports; Gunicorn is not reachable from outside.

PROJECT STRUCTURE
---

    HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker/
    ├── docker-compose.yml                 <- services web, nginx
    ├── .env.example                       <- optional settings (copy to '.env')
    ├── nginx/                             <- Nginx image
    │   ├── Dockerfile
    │   ├── 40-create-self-signed-cert.sh  <- creates the certificate on the first start
    │   └── conf.d/default.conf            <- HTTPS, redirect, static files, reverse proxy
    └── app/                               <- Django project root, Docker build context
        ├── Dockerfile
        ├── .dockerignore
        ├── entrypoint.sh                  <- secret key, migrate, collectstatic, then Gunicorn
        ├── gunicorn.conf.py
        ├── requirements.txt               <- pinned versions
        ├── manage.py
        ├── data/                          <- SQLite database + secret key (volume in the container)
        │   └── .gitignore                 <- keeps these files out of git
        ├── app/
        │   ├── settings.py                <- configured via environment variables
        │   └── urls.py
        └── core/
            ├── views.py                   <- page + health check endpoint
            ├── urls.py
            ├── tests.py
            ├── templates/core/index.html
            └── static/core/style.css

STEP BY STEP
---

01. Create the HowTo directory and generate the project skeleton with a local Python virtual environment

        ubuntu~$> mkdir "HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker"
        ubuntu~$> cd "HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate
        ubuntu~$> pip install "Django==5.2.17"
        ubuntu~$> django-admin startproject app
        ubuntu~$> cd app
        ubuntu~$> python manage.py startapp core

    Django 5.2 is a long-term support (LTS) release, which is a good fit for production.

02. Pin the dependencies in `app/requirements.txt`

    ```
    Django==5.2.17
    gunicorn==26.2.0
    ```

    Pinned versions make every image build reproducible. SQLite support is part of Python, so no database driver is needed.

03. Make `app/app/settings.py` production-ready. Every value can be set with an environment variable and has a safe default.

    ```python
    import os
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent


    def env_list(name, default=''):
        """Read a comma separated environment variable as a list."""
        return [value.strip() for value in os.environ.get(name, default).split(',') if value.strip()]


    # SECURITY WARNING: keep the secret key used in production secret!
    # Taken from DJANGO_SECRET_KEY (.env) or from the file 'data/secret_key', which
    # entrypoint.sh creates with a random key on the first start (data volume).
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or (BASE_DIR / 'data' / 'secret_key').read_text().strip()

    DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
    ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
    CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS', 'https://localhost')

    INSTALLED_APPS = [
        # ... default Django apps ...
        'core',
    ]

    # The SQLite database lives in its own directory, which is a Docker volume in the
    # container (SQLite needs write access to the directory for its journal files).
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'data' / 'db.sqlite3',
            'OPTIONS': {
                # Several Gunicorn workers write concurrently: start write transactions
                # immediately and wait up to 20 seconds for the database lock.
                'transaction_mode': 'IMMEDIATE',
                'timeout': 20,
                # WAL mode lets readers and one writer work at the same time
                'init_command': 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL',
            },
        }
    }

    STATIC_URL = 'static/'
    # 'collectstatic' copies all static files here - Nginx serves them from a shared volume
    STATIC_ROOT = BASE_DIR / 'staticfiles'

    # Nginx terminates TLS and forwards the requests to Gunicorn via plain HTTP.
    # Django trusts the 'X-Forwarded-Proto' header, which Nginx always overwrites,
    # to detect HTTPS requests.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    # The container health check calls Gunicorn directly via HTTP
    SECURE_REDIRECT_EXEMPT = [r'^healthz/$']
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))

    # Write all log messages to the console, so they show up in 'docker compose logs'
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
    ```

    - The secret key never appears in the code. It comes from `DJANGO_SECRET_KEY` or from a random key file that the container creates on its first start (see step 06).
    - `DEBUG` is off unless `DJANGO_DEBUG=1` is set explicitly.
    - Several Gunicorn worker processes share one SQLite file. `transaction_mode: IMMEDIATE` and `timeout` make a worker wait for the write lock instead of failing with `database is locked`. The WAL journal mode lets requests read while another request writes. These options need Django 5.1 or later.
    - `SECURE_PROXY_SSL_HEADER` is required behind a TLS-terminating proxy. Without it, Django would treat every request as HTTP and `SECURE_SSL_REDIRECT` would cause an endless redirect loop.
    - `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` make the browser send these cookies over HTTPS only.

    Create the directory for the database and the secret key. Its `.gitignore` keeps the directory in git, but not the files in it:

        ubuntu~$> mkdir data
        ubuntu~$> printf '*\n!.gitignore\n' > data/.gitignore

04. Add a page and a health check endpoint

    `app/core/views.py`:

    ```python
    from django.http import HttpResponse
    from django.shortcuts import render


    def index(request):
        # Show what Django sees behind the Nginx reverse proxy
        context = {
            'is_secure': request.is_secure(),
            'host': request.get_host(),
            'server': request.META.get('SERVER_SOFTWARE', '-'),
            'client_ip': request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR')),
            'forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR', '-'),
        }
        return render(request, 'core/index.html', context)


    def healthz(request):
        # Used by the health check of the 'web' container
        return HttpResponse('ok', content_type='text/plain')
    ```

    `app/core/urls.py`:

    ```python
    from django.urls import path
    from . import views


    app_name = 'core'

    urlpatterns = [
        path('', views.index, name='index'),
        path('healthz/', views.healthz, name='healthz'),
    ]
    ```

    Include the app's URLs in `app/app/urls.py`:

    ```python
    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path('', include('core.urls')),
        path('admin/', admin.site.urls),
    ]
    ```

    The template `app/core/templates/core/index.html` displays these values in a table and loads the stylesheet `app/core/static/core/style.css` with `{% static 'core/style.css' %}`.

05. Configure Gunicorn in `app/gunicorn.conf.py`. Gunicorn loads this file automatically from its working directory.

    ```python
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
    ```

06. Create the container entrypoint `app/entrypoint.sh` and make it executable (`chmod +x entrypoint.sh`)

    ```sh
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
    ```

    `umask 077` makes the key file readable for the container user only.

07. Create `app/Dockerfile`

    ```dockerfile
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
    ```

    - `requirements.txt` is copied and installed before the rest of the code, so Docker can reuse the cached dependency layer when only the code changes.
    - The container runs as the user `django`, not as `root`. When the volumes `sqlite_data` and `static_data` are created, Docker copies the owner of `/app/data` and `/app/staticfiles` from the image, so Django can write to them.

    Create `app/.dockerignore` to keep local files out of the image, including a local database in `data/`:

    ```
    __pycache__/
    *.py[cod]
    data/
    staticfiles/
    .env
    Dockerfile
    .dockerignore
    ```

08. Configure Nginx in `nginx/conf.d/default.conf` (relative to the HowTo directory)

    ```nginx
    # Gunicorn (Django) application server, reachable via the Compose network
    upstream django {
        server web:8000;
    }

    # HTTP: redirect every request to HTTPS
    server {
        listen 80;
        listen [::]:80;
        server_name _;

        return 301 https://$host$request_uri;
    }

    # HTTPS: terminate TLS, serve static files, proxy everything else to Gunicorn
    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        http2 on;
        server_name _;

        ssl_certificate     /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_session_cache   shared:SSL:10m;
        ssl_session_timeout 1d;
        ssl_session_tickets off;

        # Only enable HSTS with a certificate from a trusted CA - browsers remember
        # this header and refuse plain HTTP for the host afterwards.
        # add_header Strict-Transport-Security "max-age=31536000" always;

        client_max_body_size 10M;

        # Static files collected by 'python manage.py collectstatic' (shared volume)
        location /static/ {
            alias /app/staticfiles/;
            expires 7d;
            access_log off;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
    }
    ```

    - `web:8000` is the Compose service name of the Django container and the Gunicorn port.
    - `X-Forwarded-Proto` tells Django that the original request used HTTPS (see `SECURE_PROXY_SSL_HEADER`). Nginx always overwrites this header, so clients cannot fake it.
    - Requests to `/static/` never reach Gunicorn. Nginx reads the files from the volume that `collectstatic` filled.

09. Build an Nginx image that creates the self-signed certificate on the first start

    Create the start script `nginx/40-create-self-signed-cert.sh` and make it executable (`chmod +x nginx/40-create-self-signed-cert.sh`):

    ```sh
    #!/bin/sh
    # Creates a self-signed certificate for 'localhost' on the first start.
    # The nginx image runs all scripts in /docker-entrypoint.d/ before Nginx starts.
    set -e

    SSL_DIR=/etc/nginx/ssl

    if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
        echo "$0: using the existing certificate in $SSL_DIR"
        exit 0
    fi

    mkdir -p "$SSL_DIR"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -subj "/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

    echo "$0: created a self-signed certificate in $SSL_DIR"
    ```

    - The official nginx image runs every executable `*.sh` script in `/docker-entrypoint.d/` before Nginx starts. The prefix `40-` makes it run after the image's own scripts.
    - The certificate is stored in the volume `nginx_ssl`, so it is created only once and survives restarts.
    - Browsers only accept a certificate if the host name appears in the *Subject Alternative Name* (`-addext ...`), so the Common Name (`CN`) alone is not enough.

    Create `nginx/Dockerfile`:

    ```dockerfile
    FROM nginx:1.30-alpine

    # openssl creates the self-signed certificate on the first start
    RUN apk add --no-cache openssl

    COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

    # The nginx image runs all executable scripts in /docker-entrypoint.d/ before Nginx starts
    COPY 40-create-self-signed-cert.sh /docker-entrypoint.d/
    RUN chmod +x /docker-entrypoint.d/40-create-self-signed-cert.sh
    ```

    The Alpine-based nginx image contains no `openssl` command, so the Dockerfile installs it. The configuration is copied into the image, so rebuild after changing it (`docker compose up --build`).

10. Create `docker-compose.yml` in the HowTo directory

    ```yaml
    # Browser --HTTPS--> nginx (TLS, static files) --HTTP--> web (Gunicorn + Django + SQLite)
    # Start everything with:  docker compose up
    services:
      web:
        build: ./app
        restart: unless-stopped
        # Optional settings - the app also starts without this file (see .env.example)
        env_file:
          - path: .env
            required: false
        volumes:
          - sqlite_data:/app/data
          - static_data:/app/staticfiles
        healthcheck:
          test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz/', timeout=3)"]
          interval: 10s
          timeout: 5s
          retries: 5
          start_period: 20s

      nginx:
        build: ./nginx
        restart: unless-stopped
        ports:
          - "80:80"
          - "443:443"
        volumes:
          - nginx_ssl:/etc/nginx/ssl
          - static_data:/app/staticfiles:ro
        depends_on:
          web:
            condition: service_healthy

    volumes:
      sqlite_data:
      static_data:
      nginx_ssl:
    ```

    - `env_file` with `required: false` reads `.env` only if it exists. Without it, the defaults from `settings.py` apply. This syntax needs Docker Compose 2.24 or later.
    - `docker compose up` builds both images automatically on the first start. After changing code or configuration, rebuild them with `docker compose up --build`.
    - Only `nginx` publishes ports. Gunicorn is only reachable inside the Compose network.
    - `nginx` starts only after `web` is healthy, which means that `/healthz/` answers.
    - The volumes keep all generated data when containers are recreated or images are rebuilt:
      - `sqlite_data` holds the database and the secret key.
      - `static_data` holds the static files. It is shared: `web` writes them, and `nginx` reads them (`:ro`).
      - `nginx_ssl` holds the certificate.
    - `restart: unless-stopped` restarts crashed containers and starts the stack again after a reboot of Docker.

11. (Optional) Create `.env.example` as a template for your own settings

    ```
    # --- Django ---
    # Leave empty to use the random key that is created on the first start
    DJANGO_SECRET_KEY=
    DJANGO_DEBUG=0
    # Keep 'localhost' in the list - the health check of the 'web' container uses it.
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    DJANGO_CSRF_TRUSTED_ORIGINS=https://localhost
    DJANGO_SECURE_HSTS_SECONDS=0

    # --- Gunicorn ---
    GUNICORN_WORKERS=3
    ```

    The values match the defaults, so the app runs without a `.env` file. To change a setting, copy the template (`cp .env.example .env`) and edit `.env`. Avoid `$` in the values, because Docker Compose would try to interpolate it. `.env` is ignored by git.

12. Start the application

        ubuntu~$> docker compose up

    On the first start, the following happens automatically:
    - Docker builds both images.
    - The `web` container creates the secret key, the database and the static files.
    - The `nginx` container creates the certificate.

    The log shows lines like these:

        web-1    | Created a new secret key in data/secret_key
        nginx-1  | /docker-entrypoint.d/40-create-self-signed-cert.sh: created a self-signed certificate in /etc/nginx/ssl

    Stop the application with `ctrl-c`. To run it in the background, use `docker compose up -d`. Check it with `docker compose ps`, and follow the log with `docker compose logs -f`.

13. Create an admin user (in a second terminal, from the HowTo directory)

        ubuntu~$> docker compose exec web python manage.py createsuperuser

14. Open your browser and go to [https://localhost](https://localhost). The browser warns about the self-signed certificate. Accept the warning, and the page shows:
    - `HTTPS (request.is_secure)`: `True`
    - `Application server`: `gunicorn/26.2.0`

    [http://localhost](http://localhost) redirects to HTTPS. The [admin site](https://localhost/admin/) is styled, which shows that Nginx serves the static files.

15. Run the checks and tests inside the container

        ubuntu~$> docker compose exec web python manage.py check --deploy
        ubuntu~$> docker compose exec web python manage.py test

    `check --deploy` reports only `security.W004` (HSTS is not set), which is intended with a self-signed certificate.

16. Stop and remove the containers

        ubuntu~$> docker compose down

    Add `-v` (`docker compose down -v`) to also delete the volumes: the database, the secret key, the static files and the certificate. The next start creates new ones.

RUN THE FINISHED EXAMPLE
---

01. Start the application

        ubuntu~$> cd "HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker"
        ubuntu~$> docker compose up

02. Open your browser and go to [https://localhost](https://localhost) and accept the certificate warning.

03. Create an admin user (in a second terminal)

        ubuntu~$> docker compose exec web python manage.py createsuperuser

GOING LIVE
---

This setup is production-like. Before you use it on a real server:

- **Certificate:** Replace the self-signed certificate with one from a trusted CA (e.g. [Let's Encrypt](https://letsencrypt.org/)):
  1. Save `cert.pem` (full chain) and `key.pem` in `nginx/ssl/`, and keep the key out of git.
  2. In `docker-compose.yml`, replace the volume line `nginx_ssl:/etc/nginx/ssl` with the bind mount `./nginx/ssl:/etc/nginx/ssl:ro`. The start script then uses your certificate.
  3. Enable HSTS: uncomment `Strict-Transport-Security` in `default.conf` and set `DJANGO_SECURE_HSTS_SECONDS=31536000` in `.env`.
- **Trust the self-signed certificate locally (optional):** Copy it with `docker compose cp nginx:/etc/nginx/ssl/cert.pem ./localhost-cert.pem` and import it into the trusted root certificates of your OS or browser. After that, the browser no longer shows the warning.
- **Hosts:** Create `.env` from `.env.example`. Add your domain to `DJANGO_ALLOWED_HOSTS` and `https://<your-domain>` to `DJANGO_CSRF_TRUSTED_ORIGINS`. Keep `localhost` in `DJANGO_ALLOWED_HOSTS` for the health check.
- **Ports:** If you publish HTTPS on a port other than 443, add the port to `DJANGO_CSRF_TRUSTED_ORIGINS` (e.g. `https://localhost:8443`) and to the redirect in the HTTP server block of `default.conf`.
- **Secret key:** The generated key lives in the volume `sqlite_data`. `docker compose down -v` deletes it, which logs out all users. Alternatively, set your own key as `DJANGO_SECRET_KEY` in `.env`.
- **Database:** SQLite works well for sites with moderate traffic on a single server, because all writes are serialized. Keep the database in a Docker volume (as here) and not in a bind mount to a Windows or network drive, where file locking is unreliable. If you need several `web` containers or a high write load, switch to PostgreSQL (see HowTo 003).
- **Migrations:** `entrypoint.sh` runs `migrate` on every start of `web`. That is fine for a single container.
- **Backups:** Back up the database regularly. SQLite's backup API creates a consistent copy while the app is running:

        ubuntu~$> docker compose exec web python -c "import sqlite3; sqlite3.connect('data/db.sqlite3').backup(sqlite3.connect('data/backup.sqlite3'))"
        ubuntu~$> docker compose cp web:/app/data/backup.sqlite3 ./backup.sqlite3
