import json
from PyQt5 import QtWidgets
import os
import typing
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

import sys
from ftp_client import download_file, get_files, read_file
from imap import retrieve_mailbox

from models import User
import qz_client
import requests

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quizland")
        self.setFixedWidth(800)
        self.setFixedHeight(500)

        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

        self.mainWidget = QWidget(self)
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)

        self.user = None

        self.create_menu()
        self.show_login_dialog()
        self.show_main_window()


    def show_main_window(self):
        name_label = QLabel(f'Name: {self.user.name}')
        score_label = QLabel(f'Score: {self.user.score}')
         
        list_widget = QListWidget()

        mailbox_btn = QPushButton("MailBox")

        quiz_topics_label = QLabel(f'Quizes')

        self.files = get_files()
        print(self.files)

        for file in self.files:
            item = QListWidgetItem(file, list_widget)

        quiz_btn_layout = QHBoxLayout()
        start_quiz_btn = QPushButton("Start")
        download_quiz_btn = QPushButton("Download")
        send_by_email_btn = QPushButton("Send by Email")
        quiz_by_keyword_btn = QPushButton("Quiz By Keyword")


        quiz_btn_widget = QWidget()
        quiz_btn_widget.setLayout(quiz_btn_layout)
        quiz_btn_layout.addWidget(start_quiz_btn)
        quiz_btn_layout.addWidget(download_quiz_btn)
        quiz_btn_layout.addWidget(send_by_email_btn)
        quiz_btn_layout.addWidget(quiz_by_keyword_btn)

        start_quiz_btn.clicked.connect(lambda: self.on_start_quiz_clicked(list_widget.selectedIndexes()))
        download_quiz_btn.clicked.connect(lambda: self.on_download_quiz_clicked(list_widget.selectedIndexes()))
        quiz_by_keyword_btn.clicked.connect(self.on_quiz_by_keywork_clicked)
        send_by_email_btn.clicked.connect(lambda: self.on_send_by_email_clicked(list_widget.selectedIndexes()))

       # list_widget.itemClicked.connect(self.on_list_widget_clicked)
        mailbox_btn.clicked.connect(lambda: self.on_mailbox_clicked())

        self.layout.addWidget(name_label)
        self.layout.addWidget(score_label)
        self.layout.addWidget(mailbox_btn)
        self.layout.addWidget(QHLine())

        self.layout.addWidget(quiz_topics_label)
        self.layout.addWidget(list_widget)
        self.layout.addWidget(quiz_btn_widget)

    
  #  def __get_quiz_topics():
    def on_quiz_by_keywork_clicked(self):
        self.w = KeyworkQuizWindow()
        self.w.show()


    def on_start_quiz_clicked(self, selected_items):
        if len(selected_items) == 0:
            return

        item = selected_items[0]
        print(item.row())

        quiz = read_file(self.files[item.row()]).decode('utf-8') # todo: remove hardcoded
        print(quiz)
        quiz = json.loads(quiz)

        self.w = QuizWindow(quiz)
        self.w.show()


    def on_download_quiz_clicked(self, selected_items):
        print(selected_items)
        if len(selected_items) == 0:
            return

        item = selected_items[0]
        download_file(self.files[item.row()])


    def on_send_by_email_clicked(self, selected_items):
        if len(selected_items) == 0:
            return

        item = selected_items[0]
        filename = self.files[item.row()]

        r = requests.get('http://127.0.0.1:8000', params={'filename': filename, 'email': self.user.email})
        print('Status code: ', r.status_code)


    def on_mailbox_clicked(self):
        print("Clicked on MailBox")
        self.mb = MailBoxWindow(self.user)
        self.mb.show()

    def on_list_widget_clicked(self, item):
        print("Clicked on", item)

        self.w = QuizWindow()
        self.w.show()
    
    def create_menu(self):
        pass

    def show_login_dialog(self):
        dlg = LoginDialog(self)
        dlg.exec()



class MailBoxWindow(QWidget):
    def __init__(self, user):
        super().__init__()

        vbox = QVBoxLayout()

        self.emails = retrieve_mailbox(user)

        model = QtGui.QStandardItemModel(0, 2, self)
        model.setHorizontalHeaderLabels(['From', 'Subject'])

        for From, subject, _ in self.emails:
            it_state = QtGui.QStandardItem()
            it_state.setEditable(False)
            it_state.setCheckable(True)
            it_from = QtGui.QStandardItem(From)
            it_subject = QtGui.QStandardItem(subject)
            model.appendRow([it_from, it_subject])

        self.tableView = QtWidgets.QTableView(
            showGrid=False, selectionBehavior=QtWidgets.QAbstractItemView.SelectRows
        )

        self.tableView.setModel(model)
        self.tableView.setColumnWidth(0, 300)
        self.tableView.setColumnWidth(1, 470)
        self.tableView.clicked.connect(self.on_click)
        self.resize(800, 600)


        self.web_engine_view = QWebEngineView()

        # self.webEngineView.setHtml(html)
        layout = QVBoxLayout()
        
        
        widget = QWidget()
        layout.addWidget(self.web_engine_view)

        btn = QPushButton("Press me")
        btn.clicked.connect(self.__main_page)
        layout.addWidget(btn)

        widget.setLayout(layout)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.tableView)
        self.stacked_widget.addWidget(widget)


        vbox.addWidget(self.stacked_widget)
        self.setLayout(vbox)


      #  self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('QWebEngineView')

    
    def on_click(self, item):
        self.__email_page(item.row())
    
    def __main_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def __email_page(self, index):
        self.web_engine_view.setHtml(self.emails[index][2])
        self.stacked_widget.setCurrentIndex(1)


class KeyworkQuizWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        keyword_le = QLineEdit()
        keyword_le.setPlaceholderText('Keyword')
        start_btn = QPushButton('Start')
        start_btn.clicked.connect(lambda x: self.on_start_pressed(keyword_le))

        layout.addWidget(keyword_le)
        layout.addWidget(start_btn)

        self.setLayout(layout)

    
    def on_start_pressed(self, keyword_le):
        keyword = keyword_le.text()
        print(keyword)

        for i in reversed(range(self.layout().count())): 
            self.layout().itemAt(i).widget().setParent(None)

        self.message = qz_client.start_quiz(keyword, lambda x: self.question_available_callback(x))
        


        self.question_label = QLabel('')
        self.answer_le = QLineEdit()
        self.answer_le.setPlaceholderText('Answer')
        self.next_btn = QPushButton('Next')

        self.next_btn.clicked.connect(self.on_next_btn_pressed)

        self.layout().addWidget(self.question_label)
        self.layout().addWidget(self.answer_le)
        self.layout().addWidget(self.next_btn)

    
    def on_next_btn_pressed(self):
        answer = self.answer_le.text()
        self.answer_le.setText('')
        self.question_label.setText('')
        self.message.send_answer(answer)


    def question_available_callback(self, value):
        if isinstance(value, str):
            self.question_label.setText(value)
        else:
            self.question_label.setText(f'Correct answers: {value}')
            self.answer_le.hide()
            self.next_btn.hide()
            

class QuizWindow(QWidget):
    def __init__(self, questions: str):
        super().__init__()

        print(questions)

        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)

        self.setLayout(layout)

        print(self.layout())
        self.show_questions(questions)

    def show_questions(self, questions):
        self.button_groups = []
        for item in questions:
            group_box = QGroupBox(item['title'])
            vbox = QVBoxLayout()
            group_box.setLayout(vbox)

            group = QButtonGroup()
            self.button_groups.append(group)
            self.layout().addWidget(group_box)

            for choice in item['choices']:
                radio_btn = QRadioButton(choice)
                group.addButton(radio_btn)
                vbox.addWidget(radio_btn)

        submit_btn = QPushButton('Submit')
        submit_btn.clicked.connect(self.on_submit_pressed)

        self.layout().addWidget(submit_btn)

    def on_submit_pressed(self):
        for group in self.button_groups:
            pass
            #print(group.checkedId())



class LoginDialog(QDialog):
    def __init__(self, parent: typing.Optional[QWidget]):
        super().__init__(parent=parent)

        self.setWindowTitle("Authentication")

        QBtn = QDialogButtonBox.Ok 
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        #self.buttonBox.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout()

        login_label = QtWidgets.QLabel("Login:")
        email_label = QtWidgets.QLabel("Email")
        password_label = QtWidgets.QLabel("Password:")

        login_le = QtWidgets.QLineEdit()
        email_le = QtWidgets.QLineEdit()
        password_le = QtWidgets.QLineEdit()
        password_le.setEchoMode(QtWidgets.QLineEdit.Password)

        register_btn = QtWidgets.QPushButton("Enter")
        register_btn.clicked.connect(lambda: self.on_register_pressed(login_le.text(), email_le.text(), password_le.text()))

        layout.addWidget(login_label)
        layout.addWidget(login_le)
        layout.addWidget(email_label)
        layout.addWidget(email_le)
        layout.addWidget(password_label)
        layout.addWidget(password_le)
        layout.addWidget(register_btn)
        
        self.setLayout(layout)

        self.resize(220, 150)

    
    def on_register_pressed(self, login, email, password):
        self.parent().user = User(login, email, password)
        #self.current_user.confirmation_code = send_email(email)
        print("user registered")
        self.close()
            
    def accept(self):
        print("Accept pressed")



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()