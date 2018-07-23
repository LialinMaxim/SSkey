FROM python:3.6

RUN adduser -D sskey

WORKDIR /home/sskey

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY manage.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP manage.py

RUN chown -R sskey:sskey ./
USER sskey

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]