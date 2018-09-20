# Base container image
FROM python:3.6

# Create the new user 'sskey' with bash
# -m, --create-home    create the user's home directory
# -s, --shell SHELL    set the user’s default shell
RUN useradd -ms /bin/bash sskey

# Install or update package of postgresql-client by apt-get tool
# f-, --fix-broken     attempt to correct a system with broken dependencies in place
# -y, --yes            automatic yes to prompts
RUN apt-get update && apt-get install -f -y postgresql-client

# Set default directory that will be applied to all remaining commands
# in Dockerfile, and when the container is executing.
WORKDIR /home/sskey

# Copy requirements from project directory to WORKDIR
COPY ./app/requirements.txt requirements.txt
# Install dependencies into container
# -r, --requirement    install from the given requirements file
RUN pip install -r requirements.txt

# Copy app folder, manage.py and boot.sh from project directory to WORKDIR
COPY app app
COPY manage.py boot.sh ./
# Set executable mod for boot.sh script
RUN chmod +x boot.sh

# Set the owner of all directories and files in WORKDIR
RUN chown -R sskey:sskey ./
# Set 'sskey' user by default for any following
# instructions, and also at the start of the container
USER sskey

# Set the command that must be run at the start of the container
ENTRYPOINT ["./boot.sh"]
