import sqlite3

def get_con_sql():
    conn = sqlite3.connect('Users.db')
    return conn

def create_users_table():
    conn = get_con_sql()
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Users ')

    cur.execute('''CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY,
login TEXT NOT NULL,
password TEXT NOT NULL);''')
    conn.commit()
    cur.close()
    conn.close()
    print("db was been create")

# Вызов функции для создания таблицы
create_users_table()
