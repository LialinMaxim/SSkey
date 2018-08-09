import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DBUSER = 'postgres'
DBPASS = 'postgres'
DBHOST = '127.0.0.1'  # sskey_db container's ip address
DBPORT = '5432'
DBNAME = 'db_sskey'
engine = create_engine(
    'postgresql://{0}:{1}@{2}:{3}/{4}'.format(DBUSER, DBPASS, DBHOST, DBPORT,
                                              DBNAME))

# POSTGRES_USER = os.environ.get('POSTGRES_USER')
# POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
# POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
# POSTGRES_NAME = os.environ.get('POSTGRES_NAME')
# engine = create_engine('postgresql://%s:%s@%s/%s' % (POSTGRES_USER,
#                                                      POSTGRES_PASS,
#                                                      POSTGRES_HOST,
#                                                      POSTGRES_NAME
#                                                      ))

Session = sessionmaker(bind=engine)

Base = declarative_base()
