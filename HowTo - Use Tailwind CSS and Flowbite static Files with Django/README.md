HowTo - Use Tailwind CSS and Flowbite static Files with Django
---

This HowTo describes how to use Tailwind CSS and the Flowbite component library in Django templates. Both are downloaded once and served as local static files, so no CDN is needed at runtime and no Node.js build step is required.

###### REFERENCES
- [Tailwind CSS - Play CDN](https://tailwindcss.com/docs/installation/play-cdn)
- [Flowbite - Quickstart](https://flowbite.com/docs/getting-started/quickstart/)
- [Django documentation - How to manage static files](https://docs.djangoproject.com/en/4.2/howto/static-files/)

###### PREREQUISITES
---

Name           | Reference
-------------- | ---------------
Ubuntu         | >= 20.04.6 LTS (Focal Fossa)
Python         | >= v3.10.x
curl           | [https://curl.se/](https://curl.se/)

PROJECT STRUCTURE
---

    HowTo - Use Tailwind CSS and Flowbite static Files with Django/
    ├── requirements.txt
    └── app/                           <- Django project root
        ├── manage.py
        ├── app/
        │   ├── settings.py            <- static files configuration
        │   └── urls.py                <- includes core.urls
        ├── core/
        │   ├── urls.py
        │   ├── views.py
        │   └── templates/core/
        │       ├── base.html          <- loads Tailwind CSS + Flowbite
        │       └── index.html         <- page with Flowbite components
        └── static/
            ├── download.sh            <- downloads the CSS/JS files
            └── .gitignore             <- keeps the downloaded files out of git

STEP BY STEP
---

01. Create the HowTo directory, a Python virtual environment and install Django

        ubuntu~$> mkdir "HowTo - Use Tailwind CSS and Flowbite static Files with Django"
        ubuntu~$> cd "HowTo - Use Tailwind CSS and Flowbite static Files with Django"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate
        ubuntu~$> echo "django" > requirements.txt
        ubuntu~$> pip install -r requirements.txt

02. Create the Django project `app` and the Django app `core`

        ubuntu~$> django-admin startproject app
        ubuntu~$> cd app
        ubuntu~$> python manage.py startapp core

03. Register the app and configure the static files in `app/app/settings.py`

    ```python
    INSTALLED_APPS = [
        # ... default Django apps ...
        'core',
    ]

    STATIC_URL = 'static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    ```

    - `STATICFILES_DIRS` tells Django to serve files from the project-wide folder `app/static/`.
    - `STATIC_ROOT` is the target folder for `python manage.py collectstatic`, which is only needed for a production deployment.

04. Create the download script `app/static/download.sh`

    ```bash
    #!/bin/bash

    # Declare an array of "filename|url" pairs
    files=(
      "flowbite_v312.min.css|https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css"
      "flowbite_v312.min.js|https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js"
      "tailwind_v41.min.js|https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"
    )

    # Loop through the array and download each file
    for entry in "${files[@]}"; do
      IFS='|' read -r filename url <<< "$entry"
      echo "Downloading $filename..."
      curl -o "$filename" "$url"
    done

    echo "All files downloaded successfully."
    ```

    Run it inside `app/static/`:

        ubuntu~$> cd static
        ubuntu~$> bash download.sh
        ubuntu~$> cd ..

    To keep the downloaded files out of git, create `app/static/.gitignore`:

    ```
    *.css
    *.js
    ```

    **NOTE:** `tailwind_v41.min.js` is the Tailwind CSS browser build. It generates the CSS for the used classes in the browser at runtime, which is meant for development and prototyping.

05. Create the base template `app/core/templates/core/base.html`, which loads the static files

    ```html
    {% load static %}

    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Django + Tailwind CSS + Flowbite</title>
        <link rel="stylesheet" href="{% static 'flowbite_v312.min.css' %}">
        <script src="{% static 'tailwind_v41.min.js' %}"></script>
        <script src="{% static 'flowbite_v312.min.js' %}"></script>
    </head>

    <body class="bg-green-50">
        <div class="container mx-auto mt-4">
            {% block content %}
            {% endblock content %}
        </div>
    </body>

    </html>
    ```

    The file names must match the names used in `download.sh`. When you update Tailwind CSS or Flowbite, change both files.

06. Create the page `app/core/templates/core/index.html`

    ```html
    {% extends "core/base.html" %}

    {% block content %}
      <!-- Flowbite components, e.g. copied from https://flowbite.com/docs/ -->
    {% endblock content %}
    ```

    The example in this repo uses a Flowbite navbar, a date range picker and a footer with tooltips, all copied from the Flowbite documentation.

    **NOTE:** The templates are placed in the subfolder `templates/core/`, which avoids name clashes with templates of other apps.

07. Create the view in `app/core/views.py`

    ```python
    from django.shortcuts import render

    def index(request):
        return render(request, 'core/index.html')
    ```

08. Create `app/core/urls.py`

    ```python
    from django.urls import path
    from . import views


    app_name = 'core'

    urlpatterns = [
        path('', views.index, name='index'),
    ]
    ```

09. Include the app's URLs in `app/app/urls.py`

    ```python
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('', include('core.urls')),
        path('admin/', admin.site.urls),
    ]
    ```

10. Create the database tables and start the development server (from `app/`)

        ubuntu~$> python manage.py migrate
        ubuntu~$> python manage.py runserver

11. Open your browser and go to [http://localhost:8000](http://localhost:8000). The page shows the Flowbite components styled with Tailwind CSS.

12. Stop the server with `ctrl-c`.

RUN THE FINISHED EXAMPLE
---

01. Install all dependencies

        ubuntu~$> cd "HowTo - Use Tailwind CSS and Flowbite static Files with Django"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate
        ubuntu~$> pip install -r requirements.txt

02. Download the Tailwind CSS and Flowbite files (they are not part of the repository)

        ubuntu~$> cd app/static
        ubuntu~$> bash download.sh
        ubuntu~$> cd ..

03. Run the app

        ubuntu~$> python manage.py migrate
        ubuntu~$> python manage.py runserver

04. Open your browser and go to [http://localhost:8000](http://localhost:8000).
