#!/bin/sh
# down and rebuild the app container
echo "RESTARTING THE DOCKER app CONTAINER"
docker-compose stop app
docker-compose kill app
# -f, --force   don't ask to confirm removal
docker-compose rm -f app
docker-compose up -d --build app
#read -p "Press any key to continue... " -n 1 -s