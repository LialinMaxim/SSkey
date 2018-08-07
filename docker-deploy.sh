#!/bin/sh
# build and up the project containers in background (detach mode)
echo "DEPLOYING THE DOCKER CONTAINERS"
docker-compose down
docker-compose up -d --build
#read -p "Press any key to continue... " -n 1 -s