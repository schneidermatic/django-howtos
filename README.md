# Django-HowTos

<img src="https://github.com/schneidermatic/Django-HowTos/blob/develop/assets/images/Logo01.png" width="250">

This repository contains a collection of Django-HowTos for learning/demo purposes. Every HowTo is a self-contained Django project with its own `README.md`, which describes step by step how to build and run it.

## TABLE OF CONTENTS
<ol>
<li><a href="#tested-with">Tested With</a></li>
<li><a href="#content">Content</a></li>
<li><a href="#setup">Setup</a></li>
<li><a href="#run">Run</a></li>
<li><a href="#stop">Stop</a></li>
<li><a href="#contributing">Contributing</a></li>
</ol>

## TESTED WITH
The HowTos are tested with the following software components...

Name           | Reference
-------------- | ---------------
Windows        | >= 11
Docker Desktop | >= 4.12.0
WSL            | >= 2
Ubuntu         | >= 20.04.6 LTS (Focal Fossa)
Python         | >= 3.10
docker         | 20.10.17
docker-compose | v2.10 (HowTo 005 needs >= v2.24.0)

## CONTENT
Id  | Description                                                          | Runs with
----|----------------------------------------------------------------------|----------------
001 | [HowTo - Create an 'Hello World' App with Django](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Create%20an%20'Hello%20World'%20App%20with%20Django) | Python venv
002 | [HowTo - Use self-signed SSL Certificates in Django](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Use%20self-signed%20SSL%20Certificates%20in%20Django) | Python venv
003 | [HowTo - Dockerize a Django Web App and PostgreSQL](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Dockerize%20a%20Django%20Web%20App%20and%20PostgreSQL) | Docker Compose
004 | [HowTo - Use Tailwind CSS and Flowbite static Files with Django](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Use%20Tailwind%20CSS%20and%20Flowbite%20static%20Files%20with%20Django) | Python venv
005 | [HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Deploy%20Django%20with%20Gunicorn,%20Nginx%20and%20SSL%20in%20Docker) | Docker Compose

All changes are listed in the [CHANGELOG](CHANGELOG.md).

## SETUP
1. Clone the Django-HowTos repo

        $ cd ~
        $ git clone git@github.com:schneidermatic/Django-HowTos.git

2. Set up the shell helpers (only needed for the Python HowTos)

        $ cd ~/Django-HowTos/"HowTo - Create an 'Hello World' App with Django"
        $ source ./.apprc

    The first call creates the file `$HOME/.djangohw2s`. Set `PROJECT_HOME` in this file to the directory of the repo, e.g. `export PROJECT_HOME=$HOME/Django-HowTos`.

## RUN
The `README.md` of each HowTo contains the detailed steps. The short version:

### Python HowTos (001, 004)
1. Source the APP environment

        $ cd ~/Django-HowTos/"HowTo - Create an 'Hello World' App with Django"
        $ source ./.apprc

2. List all shorthands

        $ app_ls

         ___  _
        |   \(_)__ _ _ _  __ _ ___
        | |) | / _` | ' \/ _` / _ \
        |___// \__,_|_||_\__, \___/
           |__/          |___/
        ----------
        app_banner
        app_ls
        app_mkapp
        app_mkhw2
        app_mkpro
        app_mkvenv
        app_rmhw2
        app_rmpro
        app_rmpyc
        app_rmvenv
        app_run

3. Create the Python virtual environment and install the dependencies

        $ app_mkvenv

    `app_mkvenv` creates and activates `venv/` only if it does not exist yet. If `venv/` already exists, activate it with `source venv/bin/activate`.

4. HowTo 004 only: download the Tailwind CSS and Flowbite files

        $ cd app/static && bash download.sh && cd ../..

5. Run the APP

        $ app_run

    **NOTE:** `app_run` prints `app_setup: command not found`. The message is harmless, the server starts anyway.

6. Open your browser and go to http://localhost:8000

### HowTo 002 - HTTPS with self-signed certificates
1. Source the APP environment. This recreates the virtual environment and the certificate, and then starts the server.

        $ cd ~/Django-HowTos/"HowTo - Use self-signed SSL Certificates in Django"
        $ source ./.apprc

2. Open your browser, go to https://localhost:8000 and accept the certificate warning.

### Docker HowTos (003, 005)
- HowTo 003 - Django + PostgreSQL:

        $ cd ~/Django-HowTos/"HowTo - Dockerize a Django Web App and PostgreSQL/app"
        $ docker compose up --build

    Open http://localhost:8000/admin and log in with user `admin` and password `changeme`.

- HowTo 005 - Django + Gunicorn + Nginx + SSL:

        $ cd ~/Django-HowTos/"HowTo - Deploy Django with Gunicorn, Nginx and SSL in Docker"
        $ docker compose up

    Open https://localhost and accept the certificate warning.

## STOP
1. Stop the app with `ctrl-c`.
2. Docker HowTos only: remove the containers with `docker compose down`.

## CONTRIBUTING
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
