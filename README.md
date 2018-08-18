# SSkey
REST application 

[![Build Status](https://travis-ci.org/LialinMaxim/SSkey.svg?branch=Development)](https://travis-ci.org/LialinMaxim/SSkey)

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

##

Otherwise, for the standalone web service:

```shell
pip install -r requirements.txt
python src/manage.py runserver
```

Visit [http://localhost:5000](http://localhost:5000)

## Flask Application Structure 

```

.
├── docker-compose.yml
├── README.md
└── src
    ├── app
    │   ├── base.py
    │   ├── config.py
    │   ├── database.py
    │   ├── errors
    │   │   ├── handlers.py
    │   │   └── __init__.py
    │   ├── __init__.py
    │   ├── migrate.py
    │   ├── models.py
    │   ├── requirements.txt
    │   ├── resources.py
    │   ├── routes.py
    │   ├── shemas.py
    │   └── swagger.yaml
    ├── boot.sh
    ├── Dockerfile
    ├── __init__.py
    ├── manage.py
    └── tests
        ├── __init__.py
        └── test_basic.py

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
    # LOCAL ENVIRONMENT VALUES
    FLASK_APP=manage.py
    SECRET_KEY=m8t6u7i18s463t6lrd9eutf2
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