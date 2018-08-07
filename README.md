# SSkey
REST application 

[![Build Status](https://travis-ci.org/LialinMaxim/SSkey.svg?branch=Development)](https://travis-ci.org/LialinMaxim/SSkey)

## Getting started

Install [docker](https://docs.docker.com/engine/installation/) and run the docker-machine:

```shell
docker-machine start
```

Deploy the project:

```
docker-deploy.sh
```

Check a list containers:

```
docker ps
```

Wait a minute until the server starts and check app service logs:

```
docker-compose logs app
```

If the application was started open web-browser and visit docker-machine IP address:

[http://192.168.99.100:5000](http://192.168.99.100:5000)

Check your docker-machine IP address:

```
docker-machine ip
```

if you need to make some changes to the project without affecting the server and rebuild it use:

```
docker-app.sh
```

Otherwise, for the standalone web service:

```shell
pip install -r requirements.txt
python manage.py
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
python load_test.py
```

## Postgresql

Install [postgresql](https://www.postgresql.org/download/) and run:
```shell
python base.py # database config
python migrate.py # in order to create database
```
