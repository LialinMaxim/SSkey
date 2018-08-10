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
├── app
│   ├── base.py
│   ├── Dockerfile
│   ├── errors
│   │   ├── handlers.py
│   │   ├── __init__.py
│   ├── __init__.py
│   ├── migrate.py
│   ├── models.py
│   ├── requirements.txt
│   ├── resources.py
│   ├── routes.py
│   └── swagger.yaml
├── boot.sh
├── config.py
├── docker-compose.yml
├── environment.yaml
├── manage.py
├── README.md
└── tests
    ├── __init__.py
    ├── load_tests.py
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
pytest
```

## Postgresql

Install [postgresql](https://www.postgresql.org/download/) and run:
```shell
python base.py # database config
python migrate.py # in order to create database
```
