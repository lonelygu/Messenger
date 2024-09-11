import socket
import sqlite3
import threading
import random
from datetime import datetime

# Создание сокета
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Настройка сокета
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Получение IP адреса
IP = socket.gethostbyname(socket.gethostname())
PORT = 12333

# Привязка сокета к IP и порту
listener.bind((IP, PORT))

# Начало прослушивания
listener.listen(0)

print(f"Сервер запущен на {IP}:{PORT}")

# Список для хранения подключенных клиентов
clients = []
user_chats = {}

def handle_client(connection, address):
    print(f"Подключение от {address}")
    login = None # Инициализация переменной login
    chat_id = None
    while True:
        try:
            # Получение сообщения от клиента
            message = connection.recv(1024).decode()
            if message:
                # Разбор сообщения на команду и данные
                command, data = message.split(':', 1)
                # Проверка команды
                if command in ['REGISTER', 'LOGIN', 'CHAT', 'CREATE', 'CONNECT', 'LEAVE', 'CHANGE']:
                    if command == 'REGISTER':
                        login, password = data.split(':')
                        login = login.strip()
                        password = password.strip()
                        conn = sqlite3.connect('Users.db')
                        cur = conn.cursor()
                        cur.execute('''SELECT * FROM Users WHERE login=?''', (login,))
                        user = cur.fetchone()
                        if user:
                            connection.sendall("Пользователь уже существует".encode())
                        else:
                            cur.execute('''INSERT INTO Users (login, password) VALUES(?,?)''', (login, password))
                            conn.commit()
                            connection.sendall("Регистрация успешна".encode())
                        cur.close()
                        conn.close()
                    elif command == 'LOGIN':
                        login, password = data.split(':')
                        login = login.strip()
                        password = password.strip()
                        conn = sqlite3.connect('Users.db')
                        cur = conn.cursor()
                        cur.execute('''SELECT * FROM Users WHERE login=? AND password=?''', (login, password))
                        user = cur.fetchone()
                        if user:
                            connection.sendall(f"Вход успешен\nВаш логин: {login}".encode())
                            login = login  # Обновление переменной login
                        else:
                            connection.sendall("Неверный логин или пароль".encode())
                        cur.close()
                        conn.close()
                    elif command == 'CHAT':
                        if login is None:
                            connection.sendall(
                                "Перед оправкой сообщения в чат, вам нужно войти/зарегистрироваться".encode())
                        elif chat_id is None:
                            connection.sendall("Перед отправкой сообщений надо войти в какой-либо созданный чат,"
                                               " вы же не можете писать в пустоту hah".encode())
                        else:
                            chat_message = f"{datetime.now().strftime('%H:%M:%S')} {login}: {data}"
                            # Рассылка сообщения только пользователям в этом чате
                            for client, client_chat_id in user_chats.items():
                                if client_chat_id == chat_id:
                                    client.sendall(chat_message.encode())
                    elif command == 'CREATE':
                        name = data.strip()  # Удаление пробелов с начала и конца строки
                        if name == "":
                            connection.sendall(f"У чата должно быть название {name}".encode())
                        else:
                            chat_id = random.randint(1000, 10000)
                            connection.sendall(f"Чат {name} успешно создан - его id:{chat_id}".encode())
                            user_chats[connection] = chat_id
                    elif command == 'CONNECT':
                        chat_id = int(data)
                        if chat_id in user_chats.values():  # Проверка на существование чата
                            user_chats[connection] = chat_id
                            connection.sendall(f"Вы успешно подключились к чату {chat_id}".encode())
                        else:
                            connection.sendall("Такого чата нет в системе".encode())
                    elif command == 'LEAVE':
                        if connection in user_chats:
                            del user_chats[connection]  # Удаление пользователя из списка чатов
                            chat_id = None  # Обнуление переменной chat_id
                            connection.sendall(f"Вы успешно покинули чат".encode())
                        else:
                            connection.sendall(f"Вы не находитесь в чате".encode())
                    elif command == 'CHANGE':
                        login, old_password, new_password = data.split(':')
                        conn = sqlite3.connect('Users.db')
                        cur = conn.cursor()
                        cur.execute('''SELECT * FROM Users WHERE login=? AND password=?''', (login, old_password))
                        user = cur.fetchone()
                        if user:
                            cur.execute('''UPDATE Users SET password=? WHERE login=?''', (new_password, login))
                            conn.commit()
                            connection.sendall("Пароль успешно изменен".encode())
                        else:
                            connection.sendall("Неверный старый пароль".encode())
                        cur.close()
                        conn.close()

                else:
                    # Команда не распознана, пропускаем её
                    continue
            else:
                # Если сообщение пустое, клиент отключился
                remove_client(connection)
                break
        except:
            # Обработка ошибок, например, при отключении клиента
            remove_client(connection)
            break


def remove_client(connection):
    if connection in clients:
        clients.remove(connection)
    if connection in user_chats:
        del user_chats[connection]
    connection.close()

while True:
    connection, address = listener.accept()
    clients.append(connection)
    thread = threading.Thread(target=handle_client, args=(connection, address))
    thread.start()