# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of independent Django learning/demo projects ("HowTos"). There is no shared package, build system, linter/formatter config, or CI. Each `HowTo - <Topic>/` directory is a self-contained Django project with its own `requirements.txt` and its own `venv/` — a change in one HowTo does not apply to the others. Requirements are unpinned, except in HowTo 005.

Common layout of a HowTo:

```
HowTo - <Topic>/
  .apprc             # exports CWD=$(pwd), then sources ../.apprc (root helpers)
  README.md          # step-by-step instructions (see Conventions)
  requirements.txt   # Docker HowTos (003, 005): lives in app/ instead
  app/               # Django project root — manage.py lives here
    app/             # project package (settings.py, urls.py, ...)
    core/            # Django app (HowTos 003, 004, 005 only)
```

The project package is always named `app` and the Django app `core`. Django versions differ: Hello World/SSL were generated with 5.1, Tailwind/Docker with 4.2, and Deploy (005) with 5.2 LTS.

## Shell workflow (`.apprc` helpers)

Dev commands are bash functions defined in the root `.apprc`, loaded by sourcing a HowTo's `.apprc` **from inside that HowTo directory** (the helpers rely on `$CWD`):

```bash
cd "HowTo - Create an 'Hello World' App with Django"
source ./.apprc
app_ls        # list all app_* helpers
app_mkvenv    # create ./venv, activate it, pip install -r requirements.txt (no-op if venv exists)
app_run       # cd app && python manage.py runserver  -> http://localhost:8000
```

The first time you source it, it copies `assets/templates/djangohw2s` to `~/.djangohw2s`. You have to set `PROJECT_HOME` there to the repo root, because `app_mkhw2` and `app_rmhw2` use it.

Quirks in the root `.apprc`:
- `app_run` calls `app_setup`, which is not defined (harmless "command not found"). It does not activate the venv, so if `venv/` already exists, run `. venv/bin/activate` first. It leaves the shell in `app/`.
- `app_mkapp` requires that `app/` does *not* exist, then `cd`s into it, so it never works. Run `python manage.py startapp <name>` from `app/` instead.
- `app_mkhw2 "<name>"` copies `assets/templates/app` *into* the new directory, which produces `<name>/app/`. The template's `.apprc` therefore sources `../../.apprc`, and its README is a placeholder. That layout differs from the existing HowTos.
- Destructive helpers: `app_rmpro` deletes `app/` (the whole Django project), `app_rmhw2 "<name>"` deletes the whole HowTo directory, `app_rmvenv` deletes `venv/`.

## Running / testing without the helpers

```bash
cd "HowTo - <Topic>"
python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
cd app
python manage.py migrate
python manage.py runserver
python manage.py test                                   # all tests (only HowTo 005 has real tests)
python manage.py test core.tests.<TestCase>.<method>    # single test
```

## HowTo-specific notes

- **Hello World**: a single function view in `app/app/views.py`, SQLite.
- **Tailwind CSS + Flowbite**: the static assets are not committed (`app/static/.gitignore` ignores `*.css`/`*.js`). Fetch them before running with `cd app/static && bash download.sh`. `core/templates/core/base.html` uses the versioned filenames (`flowbite_v312.min.css`, `flowbite_v312.min.js`, `tailwind_v41.min.js`), so a version bump means updating both `download.sh` and `base.html`. Static files are served via `STATICFILES_DIRS = [BASE_DIR / 'static']`. URLs go through `include('core.urls')` (namespace `core`).
- **Self-signed SSL**: sourcing this HowTo's `.apprc` runs the whole setup, not just the helpers. It deletes `venv/`, regenerates `app/ssl/cert.pem` and `key.pem` with openssl (overwriting the committed files), reinstalls deps, migrates, and starts `runserver_plus` (django-extensions + werkzeug) on https://localhost:8000. `SECURE_SSL_REDIRECT` and the secure-cookie settings are on, so plain `runserver` over HTTP won't work.
- **Docker + PostgreSQL**: everything runs from `app/`, where `Dockerfile`, `docker-compose.yml` and `requirements.txt` live: `docker compose up --build`. The app container runs `migrate`, then the custom command `create_superuser`, then `runserver 0.0.0.0:8000`. `create_superuser` is in `core/management/commands/` and creates `admin`/`changeme` if no superuser exists.
  - `DATABASES` reads `POSTGRES_NAME/USER/PASSWORD` from the environment and hardcodes the host `postgres` (the compose service name). DB-touching `manage.py` commands therefore only work inside compose.
  - Compose mounts `.:/code` but the image's `WORKDIR` is `/app`, so code changes need a rebuild.
  - The README targets Docker Desktop with WSL 2 integration.
- **Deploy with Gunicorn, Nginx and SSL (005)**: a production-like stack. Unlike 003, `docker-compose.yml` sits at the HowTo root and `app/` is only the build context. A plain `docker compose up` must work on a fresh clone, with no setup steps. The stack is `nginx` → `web`:
  - `nginx` is its own image built from `nginx/`, with the config baked in. It handles TLS termination and the HTTP→HTTPS redirect, and serves `/static/` from the shared volume `static_data`.
  - `web` runs Gunicorn, configured in `app/gunicorn.conf.py`.
  - The database is SQLite at `app/data/db.sqlite3`, which is the volume `sqlite_data` in the container. `app/data/.gitignore` keeps the directory in git but ignores the DB files. It uses WAL mode and `transaction_mode: IMMEDIATE`, because several Gunicorn workers write concurrently.
  - `.env` is optional: `env_file` uses `required: false`, which needs Compose ≥ 2.24, and `settings.py` has defaults for everything.
  - The secret key comes from `DJANGO_SECRET_KEY`, or else from `data/secret_key`, which `app/entrypoint.sh` generates on the first start. Local `manage.py` runs outside Docker need `DJANGO_SECRET_KEY` set, e.g. `DJANGO_SECRET_KEY=x python manage.py test`.
  - `nginx/40-create-self-signed-cert.sh` runs from `/docker-entrypoint.d/` and creates `cert.pem`/`key.pem` in the volume `nginx_ssl` if they are missing.
  - Changes to `app/` or `nginx/` need `docker compose up --build`.
  - `app/entrypoint.sh` runs `migrate` + `collectstatic` on every container start. `/healthz/` is exempt from `SECURE_SSL_REDIRECT` for the container health check, which needs `localhost` in `DJANGO_ALLOWED_HOSTS`.
  - HSTS is deliberately off (self-signed cert). `check --deploy` reports only `security.W004`.

## Conventions

- Commit messages follow `* Added - ...`, `* Updated - ...`, `* Fixed - ...`, `* Deleted - ...`.
- The root `README.md` "CONTENT" table indexes the HowTos (numbered in the order they were added). Add a row there when adding a new HowTo, and an entry in `CHANGELOG.md` (Keep a Changelog format, tags like `0.2.0`).
- Each HowTo has an English `README.md` modeled on `assets/templates/app/README.md`. It has these sections: References, Prerequisites, Project Structure, Step by step, and Run the finished example.
