from mysql.connector.connection_cext import CMySQLConnection
def init(dbClient: CMySQLConnection):
    DB_NAME = "revision_app"        
    USER_TABLE_NAME = "users"
    USER_TABLE_DESC = "user VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, t_offset int, PRIMARY KEY (user)"
    TOPIC_TABLE_NAME = "topics"
    TOPIC_TABLE_DESC = f"id int AUTO_INCREMENT, topic VARCHAR(255) NOT NULL, subject VARCHAR(255) NOT NULL, do_on date, last_done date, times_done int, user varchar(255) NOT NULL, PRIMARY KEY (id), FOREIGN KEY (user) REFERENCES {USER_TABLE_NAME}(user)"

    cursor = dbClient.cursor()
    try:
        cursor.execute(f"create database if not exists {DB_NAME}")        
        cursor.execute(f"use {DB_NAME}")
        cursor.execute(f"create table if not exists {USER_TABLE_NAME}({USER_TABLE_DESC})")
        cursor.execute(f"create table if not exists {TOPIC_TABLE_NAME}({TOPIC_TABLE_DESC})")        
        dbClient.commit()        
    except Exception as e:
        print("Error in executing the query", e)
        dbClient.rollback()
    cursor.close()