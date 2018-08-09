#!/bin/sh
# down and rebuild the app container
echo "RESTARTING THE DOCKER app CONTAINER"
docker-compose stop app
docker-compose kill app
docker-compose rm app
docker-compose up -d --build app
#read -p "Press any key to continue... " -n 1 -s