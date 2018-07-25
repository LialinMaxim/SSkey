
from flask import Flask, request, Response
# from flask_sqlalchemy import SQLAlchemy



from app.models import User

# DBUSER = 'marco'
# DBPASS = 'foobarbaz'
# DBHOST = 'db'
# DBPORT = '5432'
# DBNAME = 'testdb'


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
#         user=DBUSER,
#         passwd=DBPASS,
#         host=DBHOST,
#         port=DBPORT,
#         db=DBNAME)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'foobarbaz'

# db = SQLAlchemy(app)

from app.routes import *



if __name__ == '__main__':

    # dbstatus = False
    # while dbstatus == False:
    #     try:
    #         db.create_all()
    #     except:
    #         time.sleep(2)
    #     else:
    #         dbstatus = True
    app.run(debug=True, host='127.0.0.1')
