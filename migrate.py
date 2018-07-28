from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db():
    con = None
    cur = None
    dbname = "db_sskey"
    SQL_create = "CREATE DATABASE {0};".format(dbname)
    try:
        con = connect(user='postgres', host='localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
    except:
        print("Can not connect to database: postgres")
    try:
        cur.execute(SQL_create)
        print("Database successfully created: db_sskey")
    except:
        print("Can not create a database: db_sskey. May be database already exist.")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()

def create_user():
    con = None
    cur = None
    try:
        con = connect(user='postgres', host='localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
    except:
        print("Can not connect to database: postgres")
    try:
        cur.execute("CREATE USER sskey WITH password 'sskey';")
        print("User successfully created: sskey")
    except:
        print("Can not create a new user: sskey. May be user already exist.")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()


def create_tables():
    con = None
    cur = None
    try:
        con = connect(dbname='db_sskey', user='postgres', host='localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
    except:
        print("Can not connect to database: db_sskey")
    try:
        cur.execute("CREATE TABLE users ("
                    "id serial NOT NULL,"
                    "username varchar NOT NULL,"
                    "userpass varchar NOT NULL,"
                    "email varchar,"
                    "phone varchar,"
                    "first_name varchar,"
                    "last_name varchar,"
                    "reg_date TIMESTAMP NOT NULL,"
                    "auth_time TIMESTAMP NOT NULL,"
                    "salt varchar NOT NULL,"
                    "CONSTRAINT users_pk PRIMARY KEY (id)"
                    ") WITH OIDS;")

        cur.execute("CREATE TABLE passwords ("
                    "pass_id serial NOT NULL,"
                    "user_id serial NOT NULL,"
                    "url varchar,"
                    "title varchar,"
                    "login varchar NOT NULL,"
                    "pass varchar NOT NULL,"
                    "comment TEXT,"
                    "CONSTRAINT passwords_pk PRIMARY KEY (pass_id)"
                    ") WITH OIDS;")

        cur.execute("ALTER TABLE passwords ADD CONSTRAINT passwords_fk0 "
                    "FOREIGN KEY (user_id) REFERENCES users(id);")
        print("Tables successfully created in database: db_sskey")
    except:
        print("Can not create tables in database: db_sskey. May be tables already exist.")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()


def drop_tables():
    con = None
    cur = None
    try:
        con = connect(dbname='db_sskey', user='postgres', host='localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

    except:
        print("Can not connect to database: db_sskey")
    try:
        cur.execute("ALTER TABLE passwords DROP CONSTRAINT IF EXISTS passwords_fk0;")
        cur.execute("DROP TABLE IF EXISTS users;")
        cur.execute("DROP TABLE IF EXISTS passwords;")
        print("All tables deleted in database: db_sskey")
    except:
        print("Can not delete all tables in database: db_sskey. May be tables do not exist.")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()

            
def insert_data_in_db():
    con = None
    cur = None
    try:
        con = connect(dbname='db_sskey', user='postgres', host='localhost', password='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

    except:
        print("Can not connect to database: db_sskey")
    try:
        cur.execute("INSERT INTO users VALUES (101, 'test', 'test', 'test@test.com', '380501234567', 'test', 'test', '2018-01-01 12:00:00', '2018-01-01 12:00:00', 'ffffffff');")
        cur.execute("INSERT INTO passwords VALUES (DEFAULT, 101, 'www', 'title', 'login', 'pass', 'comment');")
        cur.execute("INSERT INTO users VALUES (102, 'test2', 'test2', 'test@test.com', '380501112233', 'test2', 'test2', '2018-02-02 13:00:00', '2018-02-02 13:00:00', 'ff00ff00');")
        cur.execute("INSERT INTO passwords VALUES (DEFAULT, 102, 'www', 'title', 'login', 'pass', 'comment2');")
        print("Test data inserted successfully")
    except:
        print("Can not insert test records in tables. May be they already exist")
    finally:
        if con is not None:
            con.close()
        if cur is not None:
            cur.close()

if __name__ == "__main__":
    create_user()
    create_db()
    create_tables()
#    drop_tables()   #Uncomment it if you need delete tables 'user' and 'passwords' in databae 'db_sskey'
    insert_data_in_db()
