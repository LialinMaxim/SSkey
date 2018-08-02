#!/bin/sh
echo "STARTING SERVER"
exec python manage.py runserver -h 0.0.0.0
