import os
import json
from PyQt6 import QtCore, QtGui, QtWidgets
import wizard  # Ensure this module is available in your project
import ollama  # Ensure you have this library installed
from chatbubble import ChatBubble  # Assuming this is your custom chat bubble implementation
import addmodelwizard

class OllamaThread(QtCore.QThread):
    response_received = QtCore.pyqtSignal(str)

    def __init__(self, model, prompt):
        super().__init__()
        self.model = model
        self.prompt = prompt

    def run(self):
        try:
            response = ollama.chat(model=self.model, messages=[
                {
                    'role': 'user',
                    'content': self.prompt,
                },
            ])
            response_text = self.extract_response_text(response)
            self.response_received.emit(response_text)
        except Exception as e:
            print(e)
            self.response_received.emit(f"Error: {str(e)}")

    def extract_response_text(self, response):
        # Handle different possible structures of the response
        return str(response['message']['content'])

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 780, 520))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.layout.setObjectName("layout")

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/send.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(40, 40))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.clicked.connect(self.send_message)
        self.chat_history_file = "chat_history.json"
        self.startup()

    def startup(self):
        if os.path.exists("ollama_settings.json"):
            with open("ollama_settings.json", "r") as json_file:
                json_load = json.load(json_file)
                settings = json_load['settings']
                values = list(settings.values())
                self.model = values[0] if values else None
        else:
            wizard.run_from_mainapp()

    def send_message(self):
        prompt = self.lineEdit.text()
        if not prompt:
            return
        self.lineEdit.clear()
        message_right = ChatBubble(prompt, is_left=False)
        self.layout.addWidget(message_right)
        self.save_message(prompt, is_left=False)

        if self.model:
            self.thread = OllamaThread(self.model, prompt)
            self.thread.response_received.connect(self.display_response)
            self.thread.start()
        else:
            self.display_response("Error: No model found")

    def display_response(self, response):
        message_left = ChatBubble(response, is_left=True)
        self.layout.addWidget(message_left)
        self.save_message(response, is_left=True)

    def save_message(self, message, is_left):
        chat_message = {
            'content': message,
            'is_left': is_left
        }
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, "r") as file:
                chat_history = json.load(file)
        else:
            chat_history = []

        chat_history.append(chat_message)
        with open(self.chat_history_file, "w") as file:
            json.dump(chat_history, file, indent=4)

    def load_chat_history(self):
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, "r") as file:
                chat_history = json.load(file)
                for message in chat_history:
                    chat_bubble = ChatBubble(message['content'], is_left=message['is_left'])
                    self.layout.addWidget(chat_bubble)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BeagleAI"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
