# Django-HowTos

<img src="https://github.com/schneidermatic/Django-HowTos/blob/develop/assets/images/Logo01.png" width="250">

This repository contains a collection of Django-HowTos for learning/demo purposes.

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
docker         | 20.10.17
docker-compose | v2.10.

## CONTENT
Id  | Description                                                          
----|----------------------------------------------------------------------
001 | [HowTo - Create an 'Hello World' App with Django](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Create%20an%20'Hello%20World'%20App%20with%20Django)
002 | [HowTo - Use self-signed SSL Certificates in Django](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Use%20self-signed%20SSL%20Certificates%20in%20Django)
003 | [HowTo - Dockerize a Django Web App and PostgreSQL](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Dockerize%20a%20Django%20Web%20App%20and%20PostgreSQL)
004 | [HowTo - Use Tailwind CSS and Flowbite static Files with Django](https://github.com/schneidermatic/Django-HowTos/tree/develop/HowTo%20-%20Use%20Tailwind%20CSS%20and%20Flowbite%20static%20Files%20with%20Django)


## SETUP
1. Clone the Django-HowTos repo

        $ cd ~
        $ git clone git@github.com:schneidermatic/Django-HowTos.git

2. Select one of the HowTos i.e. 

        $ cd Django-HowTos/"HowTo - Create an 'Hello World' App with Django"
        $ source ./.apprc

3. Define the 'PROJECT_HOME' Variable in the $HOME/.djangohw2s File

## RUN
1. Source the APP Environment (again)

        $ cd Django-HowTos/"HowTo - Create an 'Hello World' App with Django"
        $ source ./.apprc

2. List all Shorthands

        $ cd Django-HowTos/"HowTo - Create an 'Hello World' App with Django"
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

4. Run the APP

        $ app_run

5. Open your Browser an go to http://localhost:8000

## STOP
1. Stop the app with 'ctrl-c' 

## CONTRIBUTING
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

