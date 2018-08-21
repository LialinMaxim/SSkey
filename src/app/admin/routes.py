from src.app import app, api
from .resources import AdminTest

api.add_resource(AdminTest, '/home')  # GET