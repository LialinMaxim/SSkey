from flask_script import Manager

from app import app
from app.base import Base, engine

manager = Manager(app)


@manager.command
def initdb():
    Base.metadata.create_all(engine)


@manager.command
def dropdb():
    Base.metadata.drop_all(engine)


@manager.command
def recreatedb():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    manager.run()
