import flet as ft
import socket
import threading

# Адрес сервера
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 12333

# Создание сокета клиента
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Глобальная переменная для хранения текущего логина пользователя
current_user = None

def main(page: ft.Page):
    global current_user

    def show_snack_bar(message):
        page.snack_bar = ft.SnackBar(ft.Text(message), open=True)
        page.update()

    def send_message(command, data):
        message = f"{command}:{data}"
        client_socket.sendall(message.encode())

    def login_button_click(e):
        send_message("LOGIN", f"{login_name.value}:{login_pass.value}")

    def register_button_click(e):
        send_message("REGISTER", f"{reg_name.value}:{reg_pass.value}")

    def send_chat_message(e):
        send_message("CHAT", chat_message.value)
        chat_message.value = ""
        page.update()

    def create_chat(e):
        send_message("CREATE", chat_name.value)

    def connect_chat(e):
        send_message("CONNECT", chat_id_field.value)

    def leave_chat(e):
        send_message("LEAVE", chat_id_field.value)

    def change_password_button_click(e):
        send_message("CHANGE", f"{current_user}:{change_old_password.value}:{change_new_password.value}")
        change_old_password.value = ""
        change_new_password.value = ""
        change_password_panel.visible = False
        page.update()

    def show_change_password_panel(e):
        change_password_panel.visible = True
        page.update()

    def handle_server_messages():
        while True:
            try:
                data_from_server = client_socket.recv(1024).decode()
                if data_from_server:
                    if data_from_server.startswith("CHAT:"):
                        chat_box.controls.append(ft.Text(data_from_server[5:]))
                        page.update()
                    else:
                        handle_server_response(data_from_server)
            except:
                break

    def handle_server_response(message):
        global current_user
        if message.startswith("Вход успешен\nВаш логин:"):
            current_user = message.split(":")[1].strip()  # Получаем логин пользователя
            show_snack_bar("Вы успешно вошли в свой аккаунт")
            page.go("/profile")
        elif message == "Вход успешен":
            show_snack_bar("Вы успешно вошли в свой профиль.")
            page.go("/profile")
        elif message == "Неверный логин или пароль":
            show_snack_bar("Проверьте введённые данные, возможно была допущена ошибка.")
        elif message == "Пароль успешно изменен":
            show_snack_bar("Вы успешно изменили пароль.")
        elif message == "Регистрация успешна":
            current_user = reg_name.value
            show_snack_bar("Вы успешно зарегистрировались, спасибо что используете мой мессенджер.")
            page.go("/profile")
        elif message == "Пользователь уже существует":
            show_snack_bar("Пользователь с таким логином уже существует.")
        elif message == "Неверный старый пароль":
            show_snack_bar("Не подходит старый пароль, проверьте введённые данные.")
        else:
            chat_box.controls.append(ft.Text(message))
            page.update()
        if "Вход успешен" in message or "Регистрация успешна" in message:
            update_profile_info()


    # Запуск потока для прослушивания сообщений от сервера
    threading.Thread(target=handle_server_messages, daemon=True).start()

    login_name = ft.TextField(label="Login", autofocus=True)
    login_pass = ft.TextField(label="Password", password=True, autofocus=True)
    reg_name = ft.TextField(label="Login", autofocus=True)
    reg_pass = ft.TextField(label="Password", password=True, autofocus=True)
    chat_message = ft.TextField(label="Enter message")
    chat_name = ft.TextField(label="Chat name")
    chat_id_field = ft.TextField(label="Chat ID")
    profile_info = ft.Text("User Profile")
    change_old_password = ft.TextField(label="Old Password", password=True, autofocus=True)
    change_new_password = ft.TextField(label="New Password", password=True, autofocus=True)

    chat_box = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    chat_container = ft.Container(content=chat_box, height=400)

    change_password_panel = ft.Column([
        change_old_password,
        change_new_password,
        ft.ElevatedButton("Change Password", on_click=change_password_button_click)
    ], visible=False)

    login_form = ft.Column([
        login_name,
        login_pass,
        ft.ElevatedButton("Login", on_click=login_button_click)
    ])

    register_form = ft.Column([
        reg_name,
        reg_pass,
        ft.ElevatedButton("Register", on_click=register_button_click)
    ])

    chat_form = ft.Column([
        chat_container,
        chat_message,
        ft.ElevatedButton("Send", on_click=send_chat_message),
        chat_name,
        ft.ElevatedButton("Create Chat", on_click=create_chat),
        chat_id_field,
        ft.ElevatedButton("Connect to Chat", on_click=connect_chat),
        ft.ElevatedButton("Leave Chat", on_click=leave_chat)
    ])

    profile_form = ft.Column([
        profile_info,
        ft.ElevatedButton("Change Password", on_click=show_change_password_panel),
        change_password_panel
    ])

    def update_profile_info():
        global current_user
        if current_user:
            profile_info.value = f"User Profile\nLogin: {current_user}"
        else:
            profile_info.value = "User Profile\nLogin: Unknown"
        page.update()

    def route_change(route):
        page.views.clear()
        if route == "/main":
            page.views.append(ft.View(route, [main_menu]))
        elif route == "/login":
            page.views.append(ft.View(route, [login_form]))
        elif route == "/register":
            page.views.append(ft.View(route, [register_form]))
        elif route == "/chat":
            page.views.append(ft.View(route, [chat_form]))
        elif route == "/profile":
            update_profile_info()
            page.views.append(ft.View(route, [profile_form]))
        else:
            page.views.append(ft.View(route, [ft.Text("404 Page Not Found")]))
        page.update()

    def on_route_change(e):
        route_change(e.route)

    page.on_route_change = on_route_change

    def go_to_login(e):
        page.go("/login")

    def go_to_register(e):
        page.go("/register")

    def go_to_chat(e):
        page.go("/chat")

    def go_to_profile(e):
        page.go("/profile")

    main_menu = ft.Column([
        ft.ElevatedButton("Go to Login", on_click=go_to_login),
        ft.ElevatedButton("Go to Register", on_click=go_to_register),
        ft.ElevatedButton("Go to Chat", on_click=go_to_chat),
        ft.ElevatedButton("Go to Profile", on_click=go_to_profile)
    ])

    page.on_route_change = on_route_change
    page.go("/main")  # Перенаправление на /main при запуске

ft.app(target=main, view=ft.WEB_BROWSER)
