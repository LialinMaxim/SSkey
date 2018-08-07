from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DBUSER = 'postgres'
DBPASS = 'postgres'
DBHOST = 'localhost' #'172.19.0.2' - sskey_db container's ip address for Docker
DBPORT = '5432'
DBNAME = 'db_sskey'
engine = create_engine(
    'postgresql://{0}:{1}@{2}:{3}/{4}'.format(DBUSER, DBPASS, DBHOST, DBPORT,
                                              DBNAME))
Session = sessionmaker(bind=engine)

Base = declarative_base()
