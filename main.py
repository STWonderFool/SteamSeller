import re
import sys
from datetime import datetime, timedelta
from json import load, dump
from pathlib import Path
from statistics import median
from traceback import format_exc
from PyQt5 import QtGui, Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QComboBox, QGridLayout, QWidget, \
    QTextBrowser, QFileDialog
from requests import Session, utils, get
from steampy.confirmation import ConfirmationExecutor
from steampy.exceptions import CaptchaRequired, InvalidCredentials
from steampy.login import LoginExecutor


def message(type_of_message, text):
    colors = {'info': 'black', 'error': 'red', 'success': 'green', 'magic': 'fuchsia'}
    ready_text = f'<font color="{colors[type_of_message]}">{text}</font>'
    return ready_text


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

        self.start_button.clicked.connect(self.start_function)

    def start_function(self):
        if self.start_button.text() == 'Start':
            self.start_button.setText('Stop')
            self.start_button.setStyleSheet('background-color: rgb(153,50,204)')
            self.status.setText(message('info', 'Starting..'))
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
        try:
            if not self.login_to_account():
                self.finish.emit()
                return
            inventory = self.get_my_inventory()
            if not inventory:
                self.finish.emit()
                return

            for item_name in sorted(inventory):
                sell_price = self.get_sell_price(item_name)
                if sell_price is None:
                    continue
                for asset_id in inventory[item_name]:
                    self.sell_in_steam(item_name, asset_id, sell_price)
        except:
            print(format_exc())

        with open('All Items ID.json', 'w') as file:
            self.all_items_id[self.game] = self.items_id
            dump(self.all_items_id, file)

        self.progress.emit(message('magic', 'Finish!'))
        self.finish.emit()

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
                self.progress.emit(message('error', response.json()))
            else:
                self.confirmation_executor.confirm_sell_listing(asset_id)
                self.progress.emit(message('info', f'{item_name} listed for {round(sell_price, 2)}'))
        except:
            self.progress.emit(message('error', f'Error listing {item_name}'))

    def get_item_id(self, item_name):
        url = f'https://steamcommunity.com/market/listings/{self.game_id}/' + item_name
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
        try:
            sell_orders = get(url).json()['sell_order_graph']
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
              f'{self.game_id}&market_hash_name=' + item_name
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
            response = get(url)
            if response.status_code != 200:
                self.progress.emit(message('error', 'Steam is not responding'))
                return False
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
            self.steam_cookies = utils.dict_from_cookiejar(self.session.cookies)
            self.session_id = self.steam_cookies['sessionid']
            self.confirmation_executor = ConfirmationExecutor(self.identity_secret, self.steam_id, self.session)
            self.progress.emit(message('magic', 'Success login!'))
            return True


app = QApplication(sys.argv)
window = SteamSeller()
window.show()
app.exec_()
