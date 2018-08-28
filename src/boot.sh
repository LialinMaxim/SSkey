#!/bin/sh
echo "Wait until the server starts..."
# 0 - Standard Input (STDIN)
# 1 - Standard Output (STDOUT)
# 2 - Standard Error (STDERR)
# > - redirect of the flow
# Redirects flow of the STDOUT and STDERR to /dev/null (nowhere)
while ! pg_isready -h ${POSTGRES_HOST} > /dev/null 2> /dev/null; do
  echo "Connecting to ${POSTGRES_HOST} Failed"
  sleep 1
done

echo "CREATING DATABASE"
python3 manage.py db init
echo "STARTING SERVER"
python3 manage.py runserver -h 0.0.0.0 # access at 192.168.99.100:5000
#read -p "Press any key to continue... " -n 1 -
