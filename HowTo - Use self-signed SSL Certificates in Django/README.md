HowTo - Use self-signed SSL Certificates in Django
---

This HowTo describes how to serve a Django app over HTTPS during development. It uses a self-signed certificate created with OpenSSL and the `runserver_plus` command from [django-extensions](https://django-extensions.readthedocs.io/).

###### REFERENCES
- [django-extensions - runserver_plus](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html)
- [Django documentation - SECURE_SSL_REDIRECT](https://docs.djangoproject.com/en/5.1/ref/settings/#secure-ssl-redirect)

###### PREREQUISITES
---

Name           | Reference
-------------- | ---------------
Ubuntu         | >= 20.04.6 LTS (Focal Fossa)
Python         | >= v3.10.x
OpenSSL        | [https://www.openssl.org/](https://www.openssl.org/)

PROJECT STRUCTURE
---

    HowTo - Use self-signed SSL Certificates in Django/
    ├── .apprc               <- sets up and starts everything (see below)
    ├── requirements.txt
    └── app/                 <- Django project root
        ├── manage.py
        ├── ssl/
        │   ├── cert.pem     <- self-signed certificate
        │   └── key.pem      <- private key
        └── app/
            ├── settings.py  <- django_extensions + HTTPS settings
            ├── urls.py
            └── views.py

STEP BY STEP
---

01. Create the HowTo directory and a Python virtual environment

        ubuntu~$> mkdir "HowTo - Use self-signed SSL Certificates in Django"
        ubuntu~$> cd "HowTo - Use self-signed SSL Certificates in Django"
        ubuntu~$> python3 -m venv venv
        ubuntu~$> source venv/bin/activate

02. Create `requirements.txt` and install the dependencies

    ```
    pyOpenSSL
    werkzeug
    django
    django-extensions
    ```

        ubuntu~$> pip install -r requirements.txt

    `django-extensions` provides the `runserver_plus` command, which is based on the Werkzeug development server and can serve HTTPS.

03. Create the Django project `app` with a 'Hello World' view

        ubuntu~$> django-admin startproject app

    Then add `app/app/views.py` and the URL route exactly as described in [HowTo 001, steps 04 and 05](../HowTo%20-%20Create%20an%20'Hello%20World'%20App%20with%20Django/README.md).

04. Create a self-signed certificate for `localhost` (valid for 10 years, private key without passphrase)

        ubuntu~$> mkdir -p app/ssl
        ubuntu~$> openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
                    -keyout app/ssl/key.pem \
                    -out app/ssl/cert.pem \
                    -subj "/C=US/ST=Illinois/L=Chicago/O=MaxPayne/OU=IT Department/CN=localhost"

05. Enable `django_extensions` and the HTTPS settings in `app/app/settings.py`

    ```python
    INSTALLED_APPS = [
        # ... default Django apps ...
        'django_extensions',
    ]

    # SSL Settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ```

    - `SECURE_SSL_REDIRECT` redirects every HTTP request to HTTPS.
    - `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` make the browser send these cookies over HTTPS only.

06. Create the database tables and start the HTTPS development server

        ubuntu~$> cd app
        ubuntu~$> python manage.py migrate
        ubuntu~$> python manage.py runserver_plus --cert-file ./ssl/cert.pem --key-file ./ssl/key.pem

07. Open your browser and go to [https://localhost:8000](https://localhost:8000). The browser warns about the self-signed certificate. Accept the warning, and the page shows `Hello, world!`.

08. Stop the server with `ctrl-c`.

    **NOTE:** The plain `runserver` command only speaks HTTP. Because of `SECURE_SSL_REDIRECT = True` every request would be redirected to `https://`, so always use `runserver_plus` with the certificate files.

RUN THE FINISHED EXAMPLE
---

01. Source the app environment

        ubuntu~$> cd "HowTo - Use self-signed SSL Certificates in Django"
        ubuntu~$> source ./.apprc

    **NOTE:** Sourcing `.apprc` performs all steps at once:
    - It deletes and recreates `venv/` and installs the dependencies.
    - It regenerates `app/ssl/cert.pem` and `app/ssl/key.pem`, overwriting the existing files.
    - It runs `migrate` and starts `runserver_plus` with the certificates.

02. Open your browser and go to [https://localhost:8000](https://localhost:8000).
