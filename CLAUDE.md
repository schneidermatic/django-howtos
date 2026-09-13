# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of independent Django learning/demo projects ("HowTos"). There is no shared package, build system, linter/formatter config, or CI. Each `HowTo - <Topic>/` directory is a self-contained Django project with its own unpinned `requirements.txt` and its own `venv/` — a change in one HowTo does not apply to the others.

Common layout of a HowTo:

```
HowTo - <Topic>/
  .apprc             # exports CWD=$(pwd), then sources ../.apprc (root helpers)
  requirements.txt   # Docker HowTo: lives in app/ instead
  app/               # Django project root — manage.py lives here
    app/             # project package (settings.py, urls.py, ...)
    core/            # Django app (Tailwind + Docker HowTos only)
```

The project package is always named `app` and the Django app `core`. Django versions differ (Hello World/SSL were generated with 5.1, Tailwind/Docker with 4.2).

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
python manage.py test                                   # all tests (tests.py files are empty stubs)
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

## Conventions

- Commit messages follow `* Added - ...`, `* Updated - ...`, `* Fixed - ...`, `* Deleted - ...`.
- The root `README.md` "CONTENT" table indexes the HowTos (numbered in the order they were added). Add a row there when adding a new HowTo.
