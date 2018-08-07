import os

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

new_user = 'sskey'
user = os.environ.get('POSTGRES_USER')
host = os.environ.get('POSTGRES_HOST')
password = os.environ.get('POSTGRES_PASS')
dbname = os.environ.get('POSTGRES_NAME')
SQL_create_db = "CREATE DATABASE {0};".format(dbname)
SQL_create_user = "CREATE USER sskey WITH password 'sskey';"
SQL_cteate_table_users = ("CREATE TABLE users ( \n"
                          "                    id serial NOT NULL, \n"
                          "                    username varchar NOT NULL, \n"
                          "                    userpass bytea NOT NULL, \n"
                          "                    email varchar, \n"
                          "                    phone varchar, \n"
                          "                    first_name varchar, \n"
                          "                    last_name varchar, \n"
                          "                    reg_date TIMESTAMP NOT NULL, \n"
                          "                    auth_time TIMESTAMP, \n"
                          "                    salt bytea NOT NULL, \n"
                          "                    CONSTRAINT users_pk PRIMARY KEY (id) \n"
                          "                    ) WITH OIDS;")

SQL_cteate_table_passwords = ("CREATE TABLE passwords ( \n"
                              "                    pass_id serial NOT NULL, \n"
                              "                    user_id serial NOT NULL, \n"
                              "                    url varchar, \n"
                              "                    title varchar,\n"
                              "                    login varchar NOT NULL, \n"
                              "                    pass varchar NOT NULL, \n"
                              "                    comment TEXT, \n"
                              "                    CONSTRAINT passwords_pk PRIMARY KEY (pass_id) \n"
                              "                    ) WITH OIDS;")

SQL_alter_table = "ALTER TABLE passwords ADD CONSTRAINT passwords_fk0 FOREIGN KEY (user_id) REFERENCES users(id);"


def create_user():
    con = None
    cur = None
    try:
        con = connect(user=user, host=host, password=password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(SQL_create_user)
        print("CREATE USER: success!!! User created: {0};".format(new_user))
    except Exception as e:
        print('CREATE USER. ERROR:', e.pgcode, e)
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def create_db():
    con = None
    cur = None
    try:
        con = connect(user=user, host=host, password=password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(SQL_create_db)
        print("CREATE DATABASE: success!!! Database created: {0};".format(
            dbname))
    except Exception as e:
        print('CREATE DATABASE. ERROR:', e.pgcode, e)
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def create_tables():
    con = None
    cur = None
    try:
        con = connect(dbname=dbname, user=user, host=host, password=password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(SQL_cteate_table_users)
        cur.execute(SQL_cteate_table_passwords)
        cur.execute(SQL_alter_table)
        print(
            "CREATE TABLES: success!!! Tables created in database: {0};".format(
                dbname))
    except Exception as e:
        print('CREATE TABLES. ERROR:', e.pgcode, e)
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def drop_tables():
    con = None
    cur = None
    try:
        con = connect(dbname=dbname, user=user, host=host, password=password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(
            "ALTER TABLE passwords DROP CONSTRAINT IF EXISTS passwords_fk0;")
        cur.execute("DROP TABLE IF EXISTS users;")
        cur.execute("DROP TABLE IF EXISTS passwords;")
        print(
            "DROP TABLE: success!!! All tables deleted in database: {0};".format(
                dbname))
    except Exception as e:
        print('DROP TABLE. ERROR:', e.pgcode, e)
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def insert_data_in_db():
    con = None
    cur = None
    try:
        con = connect(dbname=dbname, user=user, host=host, password=password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users VALUES (103, 'test', 'test', 'test@test.com', '380501234567', 'test', 'test', '2018-01-01 12:00:00', '2018-01-01 12:00:00', 'ffffffff');")
        cur.execute(
            "INSERT INTO passwords VALUES (DEFAULT, 103, 'www', 'title', 'login', 'pass', 'comment');")
        cur.execute(
            "INSERT INTO users VALUES (104, 'test2', 'test2', 'test@test.com', '380501112233', 'test2', 'test2', '2018-02-02 13:00:00', '2018-02-02 13:00:00', 'ff00ff00');")
        cur.execute(
            "INSERT INTO passwords VALUES (DEFAULT, 104, 'www', 'title', 'login', 'pass', 'comment2');")
        print(
            "INSERT DATA IN DATABASE: success!!! Test data inserted successfully in database: {0};".format(
                dbname))
    except Exception as e:
        print("INSERT DATA IN DATABASE. ERROR:", e)
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


if __name__ == "__main__":
    drop_tables()  # Uncomment function if you need delete tables 'user' and 'passwords' in databae
    create_user()
    create_db()
    create_tables()
    insert_data_in_db()  # Uncomment function if you need insert test records in tables 'user' and 'passwords' in databae
