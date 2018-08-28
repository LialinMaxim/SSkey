import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASS = os.environ.get('POSTGRES_PASS')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_NAME = os.environ.get('POSTGRES_NAME')
engine = create_engine('postgresql://%s:%s@%s/%s' % (POSTGRES_USER,
                                                     POSTGRES_PASS,
                                                     POSTGRES_HOST,
                                                     POSTGRES_NAME
                                                     ))

engine = create_engine("sqlite://")

Session = sessionmaker(bind=engine)

Base = declarative_base()
