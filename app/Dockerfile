FROM python:3.6

RUN useradd -ms /bin/bash sskey

WORKDIR /home/sskey

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY manage.py config.py boot.sh ./
RUN chmod +x boot.sh

RUN chown -R sskey:sskey ./
USER sskey

ENTRYPOINT ["./boot.sh"]
