import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QFormLayout, QTabWidget, QMessageBox, QDialog
from PyQt5.QtCore import QThread, pyqtSignal
import socket

target_host = socket.gethostbyname(socket.gethostname())
target_port = 12333

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))

class ReceiveThread(QThread):
    signal = pyqtSignal(str)
    login = pyqtSignal(str)
    def run(self):
        while True:
            try:
                message = client.recv(1024).decode()
                if message.startswith("Ваш логин:"):
                    parts = message.split(":")
                    nickname = parts[1].strip()
                    self.login.emit(nickname)
                else:
                    self.signal.emit(message)
            except:
                print("Отключен от сервера")
                break

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Чат-клиент')
        self.setGeometry(300, 300, 300, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.login_tab = QWidget()
        self.register_tab = QWidget()
        self.chat_tab = QWidget()
        self.profile_tab = QWidget()

        self.tab_widget.addTab(self.login_tab, "Вход")
        self.tab_widget.addTab(self.register_tab, "Регистрация")
        self.tab_widget.addTab(self.chat_tab, "Чат")
        self.tab_widget.addTab(self.profile_tab, "Профиль")

        self.initLoginTab()
        self.initRegisterTab()
        self.initChatTab()
        self.initProfileTab()

        self.receive_thread = ReceiveThread()
        self.receive_thread.login.connect(self.update_profile_label)
        self.receive_thread.signal.connect(self.update_text_area)
        self.receive_thread.start()

    def initLoginTab(self):
        layout = QVBoxLayout()
        self.login_tab.setLayout(layout)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.login_label = QLabel("Логин:")
        self.password_label = QLabel("Пароль:")
        self.login_line = QLineEdit()
        self.password_line = QLineEdit()
        form_layout.addRow(self.login_label, self.login_line)
        form_layout.addRow(self.password_label, self.password_line)

        self.login_button = QPushButton('Вход')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

    def initRegisterTab(self):
        layout = QVBoxLayout()
        self.register_tab.setLayout(layout)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.register_login_label = QLabel("Логин:")
        self.register_password_label = QLabel("Пароль:")
        self.register_login_line = QLineEdit()
        self.register_password_line = QLineEdit()
        form_layout.addRow(self.register_login_label, self.register_login_line)
        form_layout.addRow(self.register_password_label, self.register_password_line)

        self.register_button = QPushButton('Регистрация')
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

    def initProfileTab(self):
        layout = QVBoxLayout()
        self.profile_tab.setLayout(layout)

        self.profile_label = QLabel("Вы ещё не вошли в свой профиль")
        layout.addWidget(self.profile_label)

        # Добавление кнопки "Сменить пароль"
        self.change_password_button = QPushButton("Сменить пароль")
        self.change_password_button.clicked.connect(self.openChangePasswordDialog)
        layout.addWidget(self.change_password_button)

    def initChatTab(self):
        layout = QVBoxLayout()
        self.chat_tab.setLayout(layout)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.message_line = QLineEdit()
        layout.addWidget(self.message_line)

        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.create_chat_button = QPushButton('Создать чат')
        self.chat_name_line = QLineEdit()
        self.create_chat_button.clicked.connect(self.create_chat)
        layout.addWidget(self.chat_name_line)
        layout.addWidget(self.create_chat_button)

        self.chat_code_label = QLabel("Код чата:")
        self.chat_code_line = QLineEdit()
        layout.addWidget(self.chat_code_label)
        layout.addWidget(self.chat_code_line)

        self.connect_button = QPushButton('Подключиться к чату')
        self.connect_button.clicked.connect(self.connect_to_chat)
        layout.addWidget(self.connect_button)

        self.leave_button = QPushButton('Выйти из чата')
        self.leave_button.clicked.connect(self.leave_chat)
        layout.addWidget(self.leave_button)

    def send_message(self):
        message_text = self.message_line.text()
        full_message = f"CHAT:{message_text}".encode('utf-8')
        client.sendall(full_message)
        self.message_line.clear()

    def register(self):
        login = self.register_login_line.text()
        password = self.register_password_line.text()
        message = f"REGISTER:{login}:{password}".encode('utf-8')
        client.sendall(message)

    def login(self):
        login = self.login_line.text()
        password = self.password_line.text()
        message = f"LOGIN:{login}:{password}".encode('utf-8')
        client.sendall(message)

    def create_chat(self):
        name = self.chat_name_line.text()
        message = f"CREATE:{name}".encode('utf-8')
        client.sendall(message)

    def connect_to_chat(self):
        chat_code = self.chat_code_line.text()
        message = f"CONNECT:{chat_code}".encode('utf-8')
        client.sendall(message)

    def leave_chat(self):
        message = "LEAVE:".encode('utf-8')
        client.sendall(message)

    def openChangePasswordDialog(self):
        if self.profile_label.text() == "Вы ещё не вошли в свой профиль":
            QMessageBox.warning(self, "Ошибка", "Вы должны войти в свой профиль, чтобы изменить пароль.")
        else:
            login_parts = self.profile_label.text().split(" - ")
            if len(login_parts) > 1:
                login = login_parts[1].strip()
                old_password = "your_old_password_here"
                dialog = ChangePasswordDialog(login, old_password, "")
                dialog.exec_()

    def update_profile_label(self, nickname):
        self.profile_label.setText("Ваш логин - "+nickname)

    def update_text_area(self, message):
        if message == "Вход успешен":
            QMessageBox.information(self, "Успешный вход", "Вы успешно вошли в свой профиль.")
        elif message == "Неверный логин или пароль":
            QMessageBox.information(self, "Неверные данные", "Проверьте введённые данные,возможно была допущена ошибка")
        elif message == "Пароль успешно изменен":
            QMessageBox.information(self, "Пароль сохранён", "Вы успешно изменили пароль.")
        elif message == "Регистрация успешна":
            QMessageBox.information(self, "lonelygu", "Вы успешно зарегистрировались, спасибо что используйте мой мессенджер)")
        elif message == "Пользователь уже существует":
            QMessageBox.information(self, "Ошибка регистрации", "Пользователь с таким логином уже существует")
        elif message == "Неверный старый пароль":
            QMessageBox.information(self, "Ошибка изменения", "Не подходит старый пароль, проверьте введённые данные")
        else:
            self.text_area.append(message)

class ChangePasswordDialog(QDialog):
    def __init__(self, login, old_password, new_password):
        super().__init__()
        self.login = login
        self.old_password = old_password
        self.new_password = new_password
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.old_password_line = QLineEdit()
        self.old_password_line.setPlaceholderText("Старый пароль")
        layout.addWidget(self.old_password_line)

        self.new_password_line = QLineEdit()
        self.new_password_line.setPlaceholderText("Новый пароль")
        layout.addWidget(self.new_password_line)

        self.save_button = QPushButton("Сохранить новый пароль")
        self.save_button.clicked.connect(self.saveNewPassword)
        layout.addWidget(self.save_button)

    def saveNewPassword(self):
        old_password = self.old_password_line.text()
        new_password = self.new_password_line.text()
        login = self.login
        message = f"CHANGE:{login}:{old_password}:{new_password}".encode('utf-8')
        client.sendall(message)
        self.accept()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_client = ChatClient()
    chat_client.show()
    sys.exit(app.exec_())
