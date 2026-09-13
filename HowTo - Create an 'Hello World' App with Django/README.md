HowTo - Create an 'Hello World' App with Django
---

This HowTo describes how to create a minimal Django project that answers requests to `/` with the text `Hello, world!`.

###### REFERENCES
- [Django documentation - Writing your first Django app, part 1](https://docs.djangoproject.com/en/5.1/intro/tutorial01/)

###### PREREQUISITES
---

Name           | Reference
-------------- | ---------------
Ubuntu         | >= 20.04.6 LTS (Focal Fossa)
Python         | >= v3.10.x

PROJECT STRUCTURE
---

    HowTo - Create an 'Hello World' App with Django/
    ├── requirements.txt
    └── app/                 <- Django project root
        ├── manage.py
        └── app/             <- project package
            ├── settings.py
            ├── urls.py      <- routes '/' to the view
            ├── views.py     <- returns 'Hello, world!'
            ├── asgi.py
            └── wsgi.py

STEP BY STEP
---

01. Create the HowTo directory and a Python virtual environment

        ubuntu~$> mkdir "HowTo - Create an 'Hello World' App with Django"
        ubuntu~$> cd "HowTo - Create an 'Hello World' App with Django"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate

02. Install Django

        ubuntu~$> echo "django" > requirements.txt
        ubuntu~$> pip install -r requirements.txt

03. Create a Django project called `app`

        ubuntu~$> django-admin startproject app

    This creates `app/manage.py` and the project package `app/app/` with `settings.py`, `urls.py`, `asgi.py` and `wsgi.py`.

04. Create the view in `app/app/views.py`

    ```python
    from django.http import HttpResponse


    def index(request):
        return HttpResponse("Hello, world!")
    ```

05. Route `/` to the view in `app/app/urls.py`

    ```python
    from django.contrib import admin
    from django.urls import path
    from . import views

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', views.index)
    ]
    ```

06. Create the database tables (SQLite, `app/db.sqlite3`) and start the development server

        ubuntu~$> cd app
        ubuntu~$> python manage.py migrate
        ubuntu~$> python manage.py runserver

07. Open your browser and go to [http://localhost:8000](http://localhost:8000). The page shows `Hello, world!`.

08. Stop the server with `ctrl-c`.

    **NOTE:** To log in to the admin site at [http://localhost:8000/admin](http://localhost:8000/admin), create a user first with `python manage.py createsuperuser`.

RUN THE FINISHED EXAMPLE
---

01. Install all dependencies

        ubuntu~$> cd "HowTo - Create an 'Hello World' App with Django"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate
        ubuntu~$> pip install -r requirements.txt

02. Run the app

        ubuntu~$> cd app
        ubuntu~$> python manage.py migrate
        ubuntu~$> python manage.py runserver

03. Open your browser and go to [http://localhost:8000](http://localhost:8000).
