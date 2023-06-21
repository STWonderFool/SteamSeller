import re
import sys
from datetime import datetime, timedelta
from json import load, dump
from pathlib import Path
from random import randint
from statistics import median
from traceback import format_exc
from urllib.parse import quote
from time import sleep

from PyQt5 import QtGui, Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QComboBox, QGridLayout, QWidget, \
    QTextBrowser, QFileDialog
from requests import Session, utils, get
from steampy.confirmation import ConfirmationExecutor
from steampy.exceptions import CaptchaRequired, InvalidCredentials
from steampy.login import LoginExecutor


def get_user_agent_function():
    user_agents_list = [
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/538 (KHTML, like Gecko) Chrome/36 Safari/538',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2638.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2018.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.14',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.0.9757 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2583.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.114 Safari/537.36',
        'Mozilla/5.0 (Windows NT 8.0; WOW64) AppleWebKit/536.24 (KHTML, like Gecko) Chrome/32.0.2019.89 Safari/536.24',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.68 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36,gzip(gfe)',
        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.29 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.150 Safari/537.36',
        'Google Chrome 51.0.2704.103 on Windows 10',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2151.2 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.4.3.17934',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/49.0 Chrome/43.0.2357.138 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1204.0 Safari/537.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/533.16 (KHTML, like Gecko) Chrome/5.0.335.0 Safari/533.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1671.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36,gzip(gfe)',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/6.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/ (KHTML, like Gecko) Chrome/ Safari/',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2419.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Chrome/36.0.1985.125 CrossBrowser/36.0.1985.138 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.4 Safari/532.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36 TC2',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.45 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.45',
        'Mozilla/5.0 (Windows NT 10.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.97 Safari/537.36 Viv/1.9.818.49,gzip(gfe)',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2673.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.104 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/536.36 (KHTML, like Gecko) Chrome/67.2.3.4 Safari/536.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.61 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3258.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.41 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
        'Mozilla/5.0 (Windows NT 8.0; WOW64) AppleWebKit/536.23.38 (KHTML, like Gecko) Chrome/57.0.2740.20 Safari/536.23.38',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2851.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3608.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/536.14 (KHTML, like Gecko) Chrome/32.0.2008.86 Safari/536.14',
        'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/27.0.1453.0 Safari/537.35',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) UR/61.1.3163.34 Chrome/63.0.3239.108  Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3058.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1615.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/54.2.133 Chrome/48.2.2564.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2568.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3251.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 8.1) AppleWebKit/537.27.34 (KHTML, like Gecko) Chrome/54.0.2725.19 Safari/537.27.34',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36,gzip(gfe)',
        'Mozilla/5.0 (Windows; U; Windows 95) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.43 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Avast/70.0.917.102',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/46.0.1180.75 Safari/537.1',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3282.92 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.18 Safari/535.1',
        'Mozilla/5.0 (Windows NT 8.1; WOW64) AppleWebKit/537.34 (KHTML, like Gecko) Chrome/36.0.2039.82 Safari/537.34',
        'Mozilla/5.0 (Windows NT 6.2;en-US) AppleWebKit/537.32.36 (KHTML, live Gecko) Chrome/56.0.3075.83 Safari/537.32',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.16 Safari/537.36',
        'Mozilla/5.0 (Windows NT 7.1; en-US) AppleWebKit/535.12 (KHTML, like Gecko) Chrome/28.0.1410.43 Safari/535.12',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2531.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.775 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.18 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.355.0 Safari/533.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.139 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.69 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.1',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2714.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 7.0; Win64; x64) AppleWebKit/535.15 (KHTML, like Gecko) Chrome/53.0.2710.66 Safari/535.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2883.95 Safari/537.36',
        '24.0.1284.0.0 (Windows NT 5.1) AppleWebKit/534.0 (KHTML, like Gecko) Chrome/24.0.1284.0.3.742.3 Safari/534.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3359.181 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.102 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2427.7 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36,gzip(gfe)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.144 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2327.5 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/30.0.963.12 Safari/535.11',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0; x64) AppleWebKit/537.78 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.78',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.2.0.0 Safari/537.22',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2255.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2;en-US) AppleWebKit/537.32.36 (KHTML, live Gecko) Chrome/53.0.3036.83 Safari/537.32',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36 TungstenBrowser/2.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.20 (KHTML, like Gecko) Chrome/25.0.1330.0 Safari/537.20',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/25.0.1353.0 Safari/537.21',
        'Chrome/Soldier_0.3.0 (Windows NT 10.0)',
        'Mozilla/5.0 (Windows NT 6.1; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/stable Safari/525.13',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.4 Safari/532.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2390.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2199.73 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 6.2; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.42 Safari/534.13',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.366.2 Safari/533.4',
        'Windows / Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202 Safari/537.36',
        'Mozilla/1.0 (Windows NT 4.0, Windows NT 5.0, Windows NT 5.1, Windows NT 6.0, Windows NT 6.1, Windows NT 6.2, Windows NT 10.0) AppleWebKit (KHTML, like Gecko) Safari/1 Chrome/1',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.39 Safari/537.36']

    useragent = user_agents_list[randint(1, 99)]
    return useragent

def message(type_of_message, text):
    colors = {'info': 'black', 'error': 'red', 'success': 'green', 'magic': 'fuchsia'}
    ready_text = f'<font color="{colors[type_of_message]}">{text}</font>'
    return ready_text

def check_session(login, cookies):
    response = get('https://steamcommunity.com/', cookies=cookies)
    if login in response.text:
        return True
    else:
        return False


class Streamer(QThread):
    progress = pyqtSignal(str)
    signal = pyqtSignal()

    def __init__(self):
        super(Streamer, self).__init__()

    def run(self):
        while True:
            self.progress.emit(message('magic', 'STARTING NEW STREAM'))
            self.signal.emit()
            sleep(7200)


class SteamSeller(QWidget):
    def __init__(self):
        super(SteamSeller, self).__init__()
        self.setWindowTitle('SteamSeller')

        # Status and maFile name
        font = QtGui.QFont()
        font.setPointSize(10)
        self.status = QTextBrowser()
        self.status.setReadOnly(True)
        self.status.setFont(font)
        self.maFile_label = QLabel()
        self.maFile_label.setAlignment(Qt.Qt.AlignCenter)
        self.maFile_label.setFont(font)

        # Labels
        font.setPointSize(13)
        self.login_label = QLabel('Login')
        self.login_label.setAlignment(Qt.Qt.AlignCenter)
        self.login_label.setFont(font)
        self.password_label = QLabel('Password')
        self.password_label.setAlignment(Qt.Qt.AlignCenter)
        self.password_label.setFont(font)
        self.price_per_days_label = QLabel('Price for "N" days')
        self.price_per_days_label.setAlignment(Qt.Qt.AlignCenter)
        self.price_per_days_label.setFont(font)
        self.steam_coefficient_label = QLabel('Steam coefficient')
        self.steam_coefficient_label.setAlignment(Qt.Qt.AlignCenter)
        self.steam_coefficient_label.setFont(font)

        # LineEdits
        self.login_line_edit = QLineEdit()
        self.login_line_edit.setAlignment(Qt.Qt.AlignCenter)
        self.login_line_edit.setFont(font)
        self.password_line_edit = QLineEdit()
        self.password_line_edit.setAlignment(Qt.Qt.AlignCenter)
        self.password_line_edit.setFont(font)
        self.price_per_days_line_edit = QLineEdit()
        self.price_per_days_line_edit.setAlignment(Qt.Qt.AlignCenter)
        self.price_per_days_line_edit.setFont(font)
        self.steam_coefficient_line_edit = QLineEdit()
        self.steam_coefficient_line_edit.setAlignment(Qt.Qt.AlignCenter)
        self.steam_coefficient_line_edit.setFont(font)

        # ETC
        font.setPointSize(12)
        self.choose_mafile_button = QPushButton('Choose MaFile')
        self.choose_mafile_button.setFont(font)
        self.start_button = QPushButton('Start')
        self.start_button.setFont(font)
        self.save_button = QPushButton('Save')
        self.save_button.setFont(font)
        self.game_box = QComboBox()
        self.game_box.addItems(['CS', 'Dota', 'Rust'])
        self.game_box.setFont(font)
        self.currency_box = QComboBox()
        self.currency_box.addItems(['RUB', 'USD', 'EUR'])
        self.currency_box.setFont(font)

        # Layout
        layout = QGridLayout()
        layout.setSpacing(10)

        layout.addWidget(self.login_label, 0, 0, 1, 1)
        layout.addWidget(self.login_line_edit, 0, 1, 1, 2)
        layout.addWidget(self.password_label, 1, 0, 1, 1)
        layout.addWidget(self.password_line_edit, 1, 1, 1, 2)

        layout.addWidget(self.price_per_days_label, 0, 3, 1, 2)
        layout.addWidget(self.price_per_days_line_edit, 0, 5, 1, 1)
        layout.addWidget(self.steam_coefficient_label, 1, 3, 1, 2)
        layout.addWidget(self.steam_coefficient_line_edit, 1, 5, 1, 1)

        layout.addWidget(self.choose_mafile_button, 2, 0, 1, 2)
        layout.addWidget(self.game_box, 2, 2, 1, 3)
        layout.addWidget(self.currency_box, 2, 5, 1, 1)

        layout.addWidget(self.maFile_label, 3, 0, 1, 1)
        layout.addWidget(self.start_button, 3, 2, 1, 3)
        layout.addWidget(self.save_button, 3, 5, 1, 1)

        layout.addWidget(self.status, 4, 0, 1, 6)
        self.setLayout(layout)

        self.maFile_path = ''
        # Save & Load data
        self.load_user_data()
        self.choose_mafile_button.clicked.connect(self.choose_maFile_function)
        self.save_button.clicked.connect(self.save_function)

        self.start_button.clicked.connect(self.start_button_function)

    def start_button_function(self):
        if 'asd' in self.price_per_days_line_edit.text():
            self.price_per_days_line_edit.setText(self.price_per_days_line_edit.text().split('asd')[1].strip())
            self.streamer = Streamer()
            self.streamer.progress.connect(lambda x: self.status.append(x))
            self.streamer.signal.connect(self.start_function)
            self.streamer.start()
        else:
            self.start_function()

    def start_function(self):
        if self.start_button.text() == 'Start':
            self.start_button.setText('Stop')
            self.start_button.setStyleSheet('background-color: rgb(153,50,204)')
            self.status.append(message('info', 'Starting..'))
            self.worker = Seller(self.login_line_edit.text().strip(), self.password_line_edit.text().strip(),
                                 self.price_per_days_line_edit.text().strip(),
                                 self.steam_coefficient_line_edit.text().strip(),
                                 self.maFile_path, self.game_box.currentText(), self.currency_box.currentText())
            self.worker.progress.connect(lambda x: self.status.append(x))
            self.worker.finish.connect(self.stop_worker)
            self.worker.start()
        else:
            self.stop_worker()

    def stop_worker(self):
        self.start_button.setText('Start')
        self.start_button.setStyleSheet('background-color: light gray')
        self.worker.terminate()

    def choose_maFile_function(self):
        self.maFile_path = QFileDialog.getOpenFileName()[0]
        self.maFile_label.setText(Path(self.maFile_path).resolve().name)

    def save_function(self):
        with open('User_data.json', 'w') as file:
            data = {'login': self.login_line_edit.text().strip(), 'password': self.password_line_edit.text().strip(),
                    'price_per_days': self.price_per_days_line_edit.text().strip(),
                    'steam_coefficient': self.steam_coefficient_line_edit.text().strip(),
                    'maFile_path': self.maFile_path, 'game': self.game_box.currentText(),
                    'currency': self.currency_box.currentText()}
            dump(data, file)
        self.status.append(message('success', 'User data saved!'))

    def load_user_data(self):
        try:
            with open('User_data.json') as file:
                data = load(file)
                self.login_line_edit.setText(data['login'])
                self.password_line_edit.setText(data['password'])
                self.price_per_days_line_edit.setText(data['price_per_days'])
                self.steam_coefficient_line_edit.setText(data['steam_coefficient'])
                self.maFile_path = data['maFile_path']
                self.maFile_label.setText(Path(self.maFile_path).resolve().name)
                self.game_box.setCurrentText(data['game'])
                self.currency_box.setCurrentText(data['currency'])
                self.status.append(message('success', 'User data loaded'))
        except:
            self.status.append(message('error', 'No user data'))


class Seller(QThread):
    progress = pyqtSignal(str)
    finish = pyqtSignal()

    def __init__(self, login, password, price_per_days, steam_coefficient, maFile_path, game, currency):
        super(Seller, self).__init__()
        self.user_agent = get_user_agent_function()

        # Requirements
        self.login, self.password, self.price_per_days, self.steam_coefficient = \
            login, password, float(price_per_days), float(steam_coefficient)

        with open(maFile_path) as file:
            maFile = load(file)
            self.shared_secret, self.identity_secret = maFile['shared_secret'], maFile['identity_secret']
            self.steam_id = str(maFile['Session']['SteamID'])

        game_ids = {'cs': '730', 'dota': '570', 'rust': '252490'}
        self.game = game.lower()
        self.game_id = game_ids[self.game]

        currency_codes = {'RUB': '5', 'USD': '1', 'EUR': '3'}
        self.currency_code = currency_codes[currency]

        # ItemsID
        with open('All Items ID.json') as file:
            self.all_items_id = load(file)
            self.items_id = self.all_items_id[self.game]

        self.session = Session()

    def run(self):
        need_to_confirm_counter = 0
        try:
            if not self.get_account_cookies():
                self.finish.emit()
                return
            inventory = self.get_my_inventory()
            if not inventory:
                self.finish.emit()
                return

            response = 0
            for item_name in sorted(inventory):
                sell_price = self.get_sell_price(item_name)
                if sell_price is None:
                    continue
                for asset_id in inventory[item_name]:
                    response = self.sell_in_steam(item_name, asset_id, sell_price)
                    need_to_confirm_counter += 1
                    if need_to_confirm_counter >= 50:
                        self.progress.emit(message('magic', 'Confirming listings..'))
                        self.confirm_listings()
                        need_to_confirm_counter = 0

                    if response == 'stop':
                        break
                if response == 'stop':
                    break

            self.progress.emit(message('magic', 'Confirming last listings..'))
            self.confirm_listings()

        except:
            print(format_exc())

        with open('All Items ID.json', 'w') as file:
            self.all_items_id[self.game] = self.items_id
            dump(self.all_items_id, file)

        self.progress.emit(message('magic', 'Finish!'))
        self.finish.emit()

    def confirm_listings(self):
        try:
            self.confirmation_executor.allow_only_market_listings()
        except:
            self.progress.emit(message('error', 'Error in confirming listings'))

    def sell_in_steam(self, item_name, asset_id, sell_price):
        pure_sell_price = str(round((sell_price / 1.15) * 100))
        url = 'https://steamcommunity.com/market/sellitem/'
        headers = {'Referer': f'https://steamcommunity.com/id/{self.steam_id}/inventory'}
        data = {
            'sessionid': self.session_id,
            'appid': self.game_id,
            'contextid': '2',
            'assetid': asset_id,
            'amount': '1',
            'price': pure_sell_price
        }
        try:
            response = self.session.post(url, data=data, headers=headers)
            if not response.json()['success']:
                if 'The price entered plus the sum of outstanding listings' in response.text or \
                        'Указанная цена плюс сумма открытых лотов' in response.text:
                    self.progress.emit(message('error', response.json()))
                    return 'stop'
            else:
                self.progress.emit(message('info', f'{item_name} listed for {round(sell_price, 2)}'))
        except:
            self.progress.emit(message('error', f'Error listing {item_name}'))

    def get_item_id(self, item_name):
        url = f'https://steamcommunity.com/market/listings/{self.game_id}/' + quote(item_name)
        try:
            response = get(url)
            item_id = re.findall(r'Market_LoadOrderSpread\(\s(\d+)', response.text)[0]
            self.items_id[item_name] = item_id
            self.progress.emit(message('success', 'Got new item ID ^ ^'))
            return item_id
        except:
            self.progress.emit(message('error', 'Error getting new item ID'))
            return None

    def get_sell_price(self, item_name):
        median_price = self.get_median_price(item_name)
        if median_price is None:
            return None

        if item_name in self.items_id:
            item_id = self.items_id[item_name]
        else:
            item_id = self.get_item_id(item_name)
            if item_id is None:
                return None

        url = f'https://steamcommunity.com/market/itemordershistogram?country=RU&language=english&currency=' \
              f'{self.currency_code}&item_nameid=' + item_id

        headers = {
            'Referer': quote(f'https://steamcommunity.com/market/listings/{self.game_id}/{item_name}'),
            'User-Agent': self.user_agent
        }

        try:
            sell_orders = self.session.get(url, headers=headers).json()['sell_order_graph']
        except:
            self.progress.emit(message('error', 'Error getting steam price'))
            return None

        sell_order_graph_prices = []
        for i in sell_orders:
            sell_order_graph_prices.append(i[0])

        sell_price = None
        for i in sell_order_graph_prices:
            if i > median_price:
                sell_price = i
                break
        if sell_price is None:
            self.progress.emit(message('error', f'Cant get sell price of {item_name}'))
        return sell_price

    def get_median_price(self, item_name):
        url = f'https://steamcommunity.com/market/pricehistory/?country=RU&currency={self.currency_code}&appid=' \
              f'{self.game_id}&market_hash_name=' + quote(item_name)
        try:
            history = self.session.get(url).json()['prices']
            if not history:
                self.progress.emit(message('error', 'Steam error'))
                return None
        except:
            self.progress.emit(message('error', 'Steam error'))
            return None

        prices = []
        for i in history[-1::-1]:
            date = datetime.strptime(i[0].split(':')[0], '%b %d %Y %H')
            if datetime.now() - date > timedelta(self.price_per_days):
                break
            for j in range(int(i[2])):
                prices.append(i[1])

        if not prices:
            self.progress.emit(message('error', f'No prices in {self.price_per_days} days'))
            return None

        prices = sorted(prices, reverse=True)
        upper_prices, counter = [], 0
        for i in prices:
            if counter > len(prices) * 0.3:
                break
            counter += 1
            upper_prices.append(i)

        median_price = median(upper_prices)
        return median_price * self.steam_coefficient

    def get_my_inventory(self):
        url = f'https://steamcommunity.com/inventory/{self.steam_id}/{self.game_id}/2?l=english&count=5000'

        try:
            inventory = self.session.get(url).json()
            assets = inventory['assets']
            descriptions = inventory['descriptions']
        except:
            self.progress.emit(message('error', 'No items in your inventory'))
            return False

        blacklist = []
        try:
            with open('Blacklist.txt', encoding='utf-8') as file:
                for i in file.readlines():
                    blacklist.append(i.split('\n')[0])
        except:
            self.progress.emit(message('error', 'Error getting blacklist items'))

        inventory = {}
        for item_assets in assets:
            asset_id = item_assets['assetid']
            class_id = item_assets['classid']
            instance_id = item_assets['instanceid']
            for item_desc in descriptions:
                if class_id == item_desc['classid'] and instance_id == item_desc['instanceid']:
                    if item_desc['marketable'] == 0:
                        break
                    item_name = item_desc['market_hash_name']
                    if item_name in blacklist:
                        break

                    if item_name not in inventory:
                        inventory[item_name] = [asset_id]
                    else:
                        inventory[item_name].append(asset_id)
        return inventory

    def login_to_account(self):
        self.progress.emit(message('magic', 'Logining to account..'))
        try:
            LoginExecutor(self.login, self.password, self.shared_secret, self.session).login()

        except InvalidCredentials:
            self.progress.emit(message('error', 'Invalid login/password'))
            return False

        except CaptchaRequired:
            self.progress.emit(message('error', 'Captcha required'))
            return False

        except:
            self.progress.emit(message('error', 'Unexpected error in login'))
            return False

        else:
            self.progress.emit(message('magic', 'Success login!'))
            return True

    def get_account_cookies(self):
        with open('Sessions.json') as file:
            sessions_file = load(file)
        if self.login in sessions_file and check_session(self.login, sessions_file[self.login]):
            self.steam_cookies = sessions_file[self.login]
            utils.add_dict_to_cookiejar(self.session.cookies, self.steam_cookies)
            self.progress.emit(message('magic', 'Session is alive!'))
        else:
            if not self.login_to_account():
                return False
            with open('Sessions.json', 'w') as file:
                self.steam_cookies = utils.dict_from_cookiejar(self.session.cookies)
                sessions_file[self.login] = self.steam_cookies
                dump(sessions_file, file)

        self.session_id = self.steam_cookies['sessionid']
        self.confirmation_executor = ConfirmationExecutor(self.identity_secret, self.steam_id, self.session)
        return True


app = QApplication(sys.argv)
window = SteamSeller()
window.show()
app.exec_()
