HowTo - Dockerize a Django Web App and PostgreSQL
---

This HowTo describes how to run a Django app and a PostgreSQL database in Docker containers with Docker Compose. When the app container starts, it applies the database migrations and creates a default superuser automatically.

###### REFERENCES
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [PostgreSQL image on Docker Hub](https://hub.docker.com/_/postgres)
- [Django documentation - Writing custom django-admin commands](https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/)

###### PREREQUISITES
---

Name           | Reference
-------------- | ---------------
Ubuntu         | >= 20.04.6 LTS (Focal Fossa)
Python         | >= v3.10.x (only needed to generate the project skeleton)
Docker Desktop | >= 4.12.0 (with WSL 2 integration enabled)
docker         | [https://docs.docker.com/engine/reference/run/](https://docs.docker.com/engine/reference/run/)
docker-compose | [https://docs.docker.com/compose/reference/overview/](https://docs.docker.com/compose/reference/overview/)

PROJECT STRUCTURE
---

    HowTo - Dockerize a Django Web App and PostgreSQL/
    └── app/                          <- Django project root, Docker build context
        ├── Dockerfile
        ├── docker-compose.yml
        ├── requirements.txt
        ├── manage.py
        ├── app/
        │   └── settings.py           <- PostgreSQL connection
        └── core/
            └── management/
                └── commands/
                    └── create_superuser.py

STEP BY STEP
---

01. Create the HowTo directory and install Django locally (only needed to generate the project skeleton)

        ubuntu~$> mkdir "HowTo - Dockerize a Django Web App and PostgreSQL"
        ubuntu~$> cd "HowTo - Dockerize a Django Web App and PostgreSQL"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate
        ubuntu~$> pip install django

02. Create the Django project `app` and the Django app `core`

        ubuntu~$> django-admin startproject app
        ubuntu~$> cd app
        ubuntu~$> python manage.py startapp core

    Register the app in `app/app/settings.py`:

    ```python
    INSTALLED_APPS = [
        # ... default Django apps ...
        'core',
    ]
    ```

03. Create `app/requirements.txt` (next to `manage.py`, it is copied into the Docker image)

    ```
    django
    psycopg2
    ```

04. Configure the PostgreSQL database in `app/app/settings.py`

    ```python
    import os

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': 'postgres',
            'PORT': 5432,
        }
    }
    ```

    The credentials come from environment variables set in `docker-compose.yml`. `HOST` is the name of the Compose service, so the database is only reachable from inside the Compose network.

05. Add a management command that creates a superuser if none exists

        ubuntu~$> mkdir -p core/management/commands
        ubuntu~$> touch core/management/__init__.py core/management/commands/__init__.py

    Create `app/core/management/commands/create_superuser.py`:

    ```python
    from django.core.management.base import BaseCommand
    from django.contrib.auth.models import User

    class Command(BaseCommand):
        help = 'Create a superuser automatically if none exists'

        def handle(self, *args, **kwargs):
            # Check if a superuser already exists
            if not User.objects.filter(is_superuser=True).exists():
                # If no superuser exists, create one
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='changeme'  # Replace with a secure password
                )
                self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
            else:
                self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
    ```

    Django registers the command under its file name, so it runs as `python manage.py create_superuser`.

06. Create `app/Dockerfile`

    ```dockerfile
    FROM python:3.10
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install -r requirements.txt
    COPY . .
    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    ```

    The server binds to `0.0.0.0` so that it is reachable from outside the container.

07. Create `app/docker-compose.yml`

    ```yaml
    services:
      postgres:
        image: postgres
        volumes:
          - postgres_data:/var/lib/postgresql/data
        environment:
          - POSTGRES_DB=postgres
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=postgres
        ports:
          - "5432:5432"
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
          interval: 10s
          timeout: 5s
          retries: 5
      app:
        build: .
        command: >
          sh -c "python manage.py migrate &&
                 python manage.py create_superuser &&
                 python manage.py runserver 0.0.0.0:8000"
        volumes:
          - .:/code
        ports:
          - "8000:8000"
        environment:
          - POSTGRES_NAME=postgres
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=postgres
        depends_on:
          postgres:
            condition: service_healthy

    volumes:
      postgres_data:

    networks:
      postgres:
        driver: bridge
    ```

    - The `postgres` service stores its data in the named volume `postgres_data`, so the data survives container restarts.
    - The `healthcheck` runs `pg_isready`. `$$` escapes the `$`, so the variables are expanded inside the container and not by Compose.
    - `depends_on` with `condition: service_healthy` starts the app only after the database accepts connections.
    - The app's `command` replaces the Dockerfile's `CMD`. It applies the migrations, creates the superuser and starts the server.

08. Build the images and start the containers

        ubuntu~$> docker compose up --build

09. Open your browser and go to [http://localhost:8000/admin](http://localhost:8000/admin). Log in with user `admin` and password `changeme`.

    **NOTE:** The project defines no view for `/`, so [http://localhost:8000](http://localhost:8000) shows Django's 404 page.

10. Stop the containers with `ctrl-c`, then remove them

        ubuntu~$> docker compose down

    Add `-v` (`docker compose down -v`) to also delete the database volume.

    **NOTE:** The bind mount `.:/code` does not match the image's `WORKDIR /app`, so code changes are not picked up by the running container. Rebuild with `docker compose up --build` after changing the code.

RUN THE FINISHED EXAMPLE
---

01. Build and start the containers

        ubuntu~$> cd "HowTo - Dockerize a Django Web App and PostgreSQL/app"
        ubuntu~$> docker compose up --build

02. Open your browser and go to [http://localhost:8000/admin](http://localhost:8000/admin) (user `admin`, password `changeme`).
