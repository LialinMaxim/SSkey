#!/bin/sh
echo "Wait a minute until the server starts..."
sleep 1m
echo "CREATING DATABASE"
python3 manage.py db init
echo "STARTING SERVER"
python3 manage.py runserver -h 0.0.0.0 # access at 192.168.99.100:5000
#read -p "Press any key to continue... " -n 1 -
