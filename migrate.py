from psycopg2 import connect
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db():
    con = None
    cur = None
    dbname = "db_test2"
    SQL_create="CREATE DATABASE {0};".format(dbname)
    try:
        con = connect(user='postgres3', host = 'localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
    except:
        print("Can not connect to database: postgres")
    finally:
        if con is not None:
            con.close()
    try:
        cur.execute(SQL_create)
    except:
        print("Can not create a database: db_sskey")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()
            

def create_tables():
    try:
        con = connect(dbname='db_test2', user='postgres', host = 'localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
    except:
        print("Can not connect to database: db_sskey") 
    try:
        cur.execute("CREATE TABLE users ("
                   "id serial NOT NULL,"
                   "username varchar NOT NULL,"
                   "userpass varchar NOT NULL,"
                   "email varchar NOT NULL,"
                   "phone varchar,"
                   "first_name varchar,"
                   "last_name varchar,"
                   "reg_date TIMESTAMP NOT NULL,"
                   "salt varchar NOT NULL,"
                   "CONSTRAINT users_pk PRIMARY KEY (id)"
                   ") WITH OIDS;")

        cur.execute("CREATE TABLE passwords ("
                    "user_id serial NOT NULL,"
                    "host varchar NOT NULL,"
                    "login varchar NOT NULL,"
                    "pass varchar NOT NULL,"
                    "comment TEXT,"
                    "CONSTRAINT passwords_pk PRIMARY KEY (user_id)"
                    ") WITH OIDS;")

        cur.execute("ALTER TABLE passwords ADD CONSTRAINT passwords_fk0 "
                    "FOREIGN KEY (user_id) REFERENCES users(id);")
    except:
        print("Can not create tables in database: db_sskey")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()   

if __name__ == "__main__":
    create_db()
    create_tables()
