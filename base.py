from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DBUSER = 'postgres'
DBPASS = 'postgres'
DBHOST = '127.0.0.1'
DBPORT = '5432'
DBNAME = 'bd_sskey'
engine = create_engine('postgresql://{0}:{1}@{2}:{3}/{4}'.format(DBUSER, DBPASS, DBHOST, DBPORT, DBNAME))
Session = sessionmaker(bind=engine)

Base = declarative_base()