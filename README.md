# SSkey
[![Build Status](https://travis-ci.org/LialinMaxim/SSkey.svg?branch=Development)](https://travis-ci.org/LialinMaxim/SSkey)

This is REST application for storing user's passwords for Internet resources. In the application built-in Swagger UI for working with the application. Project is based on Flask framework.


SSkey project main features:

* built-in swagger ui
* authentication and authorization with session
* creating passwords
* password encryption
* user’s passwords list
* search password by its description
* admin resource for managing users

Here is how it looks at [http://sskey.pythonanywhere.com/](http://sskey.pythonanywhere.com/):

![sskey](https://raw.githubusercontent.com/LialinMaxim/SSkey/sandbox/src/app/static/swagger_sskey.png)


## Getting started

1. Install [Docker](https://docs.docker.com/engine/installation/) and run the docker-machine:

    ```shell
    docker-machine start
    ```

2. Deploy the project:

    ```shell
    docker-deploy.sh
    ```

3. Check a list containers:

    ```shell
    docker ps
    ```

4. Wait a minute until the server starts and check app service logs:

    ```shell
    docker-compose logs app
    ```

5. If the application was started visit a default docker-machine IP address:

    [http://192.168.99.100:5000](http://192.168.99.100:5000)

If you need to check your docker-machine IP address use:

```shell
docker-machine ip
```

If you need to make some changes to the project without affecting the server and rebuild it use:

```shell
docker-app.sh
```

## Local launch

1. Create `.env` file in `src/app` folder and write the environment variables into it.

2. Environment variables for application:

    ```shell
    SECRET_KEY=yor_secret_key
    ``` 
    
    Environment variables for your PostgreSQL database:
    
    ```shell
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASS=your_postgres_password
    POSTGRES_NAME=your_postgres_db_name
    POSTGRES_HOST=localhost
    ``` 

3. Install dependencies:

    ```shell
    pip install -r src/app/requirements.txt
    ```

4. Run the application:

    ```shell
    python src/manage.py runserver
    ```
    
5. Initialise Data Base:

    ```shell
    python src/manage.py db init
    ```
    
6. Visit [http://localhost:5000](http://localhost:5000)

## Flask Application Structure 

```

.
├── docker-app.sh
├── docker-compose.yml
├── docker-deploy.sh
├── README.md
├── src
│   ├── app
│   │   ├── api.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── requirements.txt
│   │   ├── resources.py
│   │   ├── routes.py
│   │   ├── scheme.py
│   │   ├── swagger_models.py
│   │   └── swagger.yaml
│   ├── boot.sh
│   ├── Dockerfile
│   ├── __init__.py
│   ├── manage.py
│   └── tests
│       ├── __init__.py
│       ├── requests
│       │   ├── admin_requests.py
│       │   ├── basic_requests.py
│       │   ├── __init__.py
│       │   ├── login_requests.py
│       │   └── user_requests.py
│       ├── test_admin_routes.py
│       ├── test_basic_routes.py
│       ├── test_login_routes.py
│       ├── test_user_passwords.py
│       ├── test_user_routes.py
│       └── user_passwords_requests.py
└── sskey.env

```

## Development

Create a new branch off the **develop** branch for features or fixes.

After making changes rebuild images and run the app:

```shell
docker-compose build
docker-compose run -p 5000:5000 web python manage.py
```

## Tests

Standalone unit tests run with:

```shell
python -m pytest src/tests
```

## Standalone installation of Database PostgreSQL

1. Install [postgresql](https://www.postgresql.org/download/)

2. Create environment file .env and put into /src/app directory with content:

    ```shell
    SECRET_KEY=wizard380684096936
    POSTGRES_USER=postgres
    POSTGRES_PASS=postgres
    POSTGRES_HOST=localhost
    POSTGRES_NAME=db_sskey
    ```
3. Change database config if you need in file:

    ```shell
    src/app/base.py
    ```

4. Run the database initialization using one of this commands:
- drop old and create new database, insert tables from SQLAlchemy models:
    ```shell
    python manage.py db init 
    ```
- create database if not exist and insert tables from SQLAlchemy models:
    ```shell
    python manage.py db create
    ```
- drop tables from database:
    ```shell
    python manage.py db drop
    ```
- drop old tables and create new tables in database from SQLAlchemy models:
    ```shell
    python manage.py db update
    ```
- standalone manual creation of database
    ```shell
    python migrate.py
    ```