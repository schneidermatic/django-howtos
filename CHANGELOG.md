# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-13

### Added
- HowTo 005 - Deploy Django with Gunicorn, Nginx and SSL in Docker (production-like Docker Compose stack: Nginx with TLS termination and static files, Gunicorn, SQLite in a Docker volume). It starts with a plain `docker compose up`: the secret key and the self-signed certificate are created automatically on the first start.

### Changed
- `README.md`:
  - The RUN section now has a quick start for every HowTo type (Python venv, HowTo 002, Docker).
  - The steps for the `.apprc` helpers are corrected: `app_mkvenv` has to run before `app_run`.
  - The content table has a new "Runs with" column and a link to the CHANGELOG.
- `CLAUDE.md`: added notes for HowTo 005.

## [0.2.0] - 2026-09-13

### Added
- `README.md` in each HowTo directory with step-by-step instructions (in English).

## [0.1.0] - 2026-09-13

First tagged release, covering all HowTos added so far.

### Added
- HowTo 001 - Create an 'Hello World' App with Django.
- HowTo 002 - Use self-signed SSL Certificates in Django (`runserver_plus` with generated self-signed certificates).
- HowTo 003 - Dockerize a Django Web App and PostgreSQL (Docker Compose setup with automatic superuser creation).
- HowTo 004 - Use Tailwind CSS and Flowbite static Files with Django (`download.sh` fetches the static assets).
- Shared `.apprc` shell helpers (`app_*`) and the HowTo project template in `assets/templates/`.
- `CLAUDE.md` with guidance for Claude Code.
- `CHANGELOG.md`.

### Changed
- `README.md`: the content table now lists all four HowTos.
