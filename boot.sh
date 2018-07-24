#!/bin/sh
echo "Starting entry point"
#source venv/Scripts/activate.bat
#flask db upgrade
#flask translate compile

echo "Starting server"
python manage.py runserver 0.0.0.0:5000
