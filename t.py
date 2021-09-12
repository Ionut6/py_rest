import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        if c:
            print("Tabela inserata", create_table_sql)
        else:
            print("Nu este inserta tabela")
    except Error as e:
        print(e)

database = r"E:\pythonsqlite.db"

sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS image (
                                        id integer PRIMARY KEY,
                                        binImage text NOT NULL,
                                        format text
                                    ); """


# create a database connection
conn = create_connection(database)
cursor = conn.cursor()
if conn is not None:
    #create projects table
    print("Reusit")
    create_table(conn, sql_create_projects_table)
    cursor.execute("Select * from image;")
    print(cursor.fetchall())

try:
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    print("Connected to SQLite")

    sqlite_insert_with_param = """INSERT INTO image
                          (id,binImage,format) 
                          VALUES (?,?,?);"""

    data_tuple = (1, "binImage", "format")
    cursor.execute(sqlite_insert_with_param, data_tuple)
    sqliteConnection.commit()
    print("Python Variables inserted successfully into SqliteDb_developers table")

    cursor.close()

except sqlite3.Error as error:
    print("Failed to insert Python variable into sqlite table", error)
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print("The SQLite connection is closed")
