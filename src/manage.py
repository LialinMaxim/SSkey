from flask_script import Manager
from app.database import manager as database_manager
from app import app

manager = Manager(app)

manager.add_command("db", database_manager)

if __name__ == "__main__":
    manager.run()
