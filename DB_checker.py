import sqlite3

def main():
    while True:
        command = input("Введите команду (для получения новой таблицы, 'new'): ")
        if command.lower() == 'new':
            conn = sqlite3.connect('Users.db')
            cur = conn.cursor()
            cur.execute('''SELECT * FROM Users''')
            users = cur.fetchall()
            cur.close()
            conn.close()

            print("(ID,'login', 'password')")
            for x in users:
                print(str(x))

if __name__ == "__main__":
    main()
