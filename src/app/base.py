from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from . import app

engine = create_engine('%s://%s:%s@%s/%s' % (app.config['DATABASE'],
                                             app.config['DB_USER'],
                                             app.config['DB_PASS'],
                                             app.config['DB_HOST'],
                                             app.config['DB_NAME']
                                             ))

"""scoped_session provides scoped management of Session objects."""
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
