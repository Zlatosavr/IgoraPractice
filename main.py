import sqlite3
import sys
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QLineEdit


class Auth(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.DB = DataBase()
        self.ui = uic.loadUi('forms/auth.ui', self)
        self.ui.show()
        self.btn_enter.clicked.connect(self.auth)
        self.btn_pas.clicked.connect(self.hide_pas)
        self.hide_password = True
    
    def hide_pas(self):
        self.password = self.ui.edit_password
        if self.hide_password:
            self.password.setEchoMode(QLineEdit.Normal)
            self.hide_password = False
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.hide_password = True

    def auth(self):
        log = self.ui.edit_login.text()
        password = self.ui.edit_password.text()
        data = self.DB.get_auth_info(log, password)     # если неправильные данные, то вернет False
        if data:
            self.DB.add_entry(datetime.now().strftime('%d.%m.%y %H:%M'), log, True)
            self.ui.hide()
            post, full_name = data[0]
            main_win = Window(post, full_name)
            main_win.setWindowTitle('Курорт Игора')

            main_win.exec()
        else:
            self.error.setStyleSheet("color:red")  # Изменение цвета шрифта на зелёный
            self.error.setText('Ошибка входа')
            self.DB.add_entry(datetime.now().strftime('%d.%m.%y %H:%M'), log, False)


class Clients(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = uic.loadUi('forms/table_client.ui', self)

        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName("igora.db")
        con.open()

        self.model = QSqlQueryModel()   # модель (таблица) без редактирования данных
        self.model.setQuery("SELECT * FROM client")
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


class Services(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = uic.loadUi('forms/table_serv.ui', self)

        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName("igora.db")
        con.open()

        self.model = QSqlQueryModel()   # модель (таблица) без редактирования данных
        self.model.setQuery("SELECT * FROM service")
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


class Order(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = uic.loadUi('forms/table_ord.ui', self)

        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName("igora.db")
        con.open()

        self.model = QSqlQueryModel()   # модель (таблица) без редактирования данных
        self.model.setQuery("SELECT * FROM order1")
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


class Window(QDialog):
    def __init__(self, post, fullName, parent = None):
        super().__init__(parent)
        self.DB = DataBase()
        self.ui = uic.loadUi('forms/main.ui', self)
        self.ui.lbl_role.setText('Роль: ' + post + '\n' + 'ФИО: ' + fullName)
        self.ui.btn_clients.clicked.connect(self.clients)
        self.ui.btn_serv.clicked.connect(self.sevices)
        self.ui.btn_add_order.clicked.connect(self.add_order)
        self.ui.btn_ord.clicked.connect(self.orders)
        self.ui.btn_exit.clicked.connect(self.exit)

        self.ui.btn_service.clicked.connect(self.report_service)
        self.ui.btn_order.clicked.connect(self.report_order)

        if post == 'Продавец' or post == 'Старший смены':
            self.ui.lbl_role.setText('Роль: ' + post + '\n' + 'ФИО: ' + fullName)
            self.ui.stackedWidget.setCurrentIndex(0)
        elif post == 'Администратор':
            self.ui.lbl_role2.setText('Роль: ' + post + '\n' + 'ФИО: ' + fullName)
            self.ui.stackedWidget.setCurrentIndex(1)
            self.update_table_history()

    def exit(self):
        self.close()
        auth = Auth()
		
    def report_service(self):
        s_date = self.ui.start_date.text().split('.')[::-1]
        e_date = self.ui.end_date.text().split('.')[::-1]
        data = self.DB.get_order()
        new_data = {}
        for d in data:
            if d[2].split('.')[-1::-1] <= e_date and d[2].split('.')[-1::-1] >= s_date:
                try:
                    new_data[d[2]] = str(int(new_data[d[2]])+len(d[5].split(',')))
                except Exception:
                    new_data[d[2]] = str(len(d[5].split(',')))
        self.table_update(list(new_data.items()), ['Дата', 'Кол-во заказов'])

    def report_order(self):
        s_date = self.ui.start_date.text().split('.')[::-1]
        e_date = self.ui.end_date.text().split('.')[::-1]
        data = self.DB.get_order()
        new_data = {}
        for d in data:
            if d[2].split('.')[-1::-1] <= e_date and d[2].split('.')[-1::-1] >= s_date:
                try:
                    new_data[d[2]] = str(int(new_data[d[2]])+1)
                except Exception:
                    new_data[d[2]] = '1'
        self.table_update(list(new_data.items()), ['Дата', 'Кол-во оказанных услуг'])

    def table_update(self, data, titels):
        numrows = len(data)
        numcols = len(titels)
        self.ui.tableWidget.setColumnCount(numcols)
        self.ui.tableWidget.setRowCount(numrows)
        self.ui.tableWidget.setHorizontalHeaderLabels(titels)

        for row in range(numrows):
            for column in range(numcols):
                self.ui.tableWidget.setItem(row, column, QTableWidgetItem((data[row][column])))
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def update_table_history(self):
        con = QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('igora.db')
        con.open()

        model = QSqlQueryModel()    # без редактирования
        model.setQuery('SELECT * FROM history')
        self.ui.tableView.setModel(model)
        self.ui.tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def add_order(self):
        service = self.ui.edit_service.text()
        client = self.ui.edit_client.value()
        order = self.ui.edit_order.text()
        time = self.ui.edit_time.text()
        self.DB.add_order(service,client,order,time)

    def clients(self):
        clients = Clients()
        clients.setWindowTitle('Клиенты')

        clients.exec()

    def sevices(self):
        sevices = Services()
        sevices.setWindowTitle('Услуги')

        sevices.exec()

    def orders(self):
        orders = Order()
        orders.setWindowTitle('Услуги')

        orders.exec()


class DataBase():
    def __init__(self):
        self.con = sqlite3.connect('igora.db')

    def get_order(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM order1")
        return cur.fetchall()

    def add_entry(self, time, log, try_entry):
        cur = self.con.cursor()
        cur.execute("INSERT INTO history VALUES (?,?,?)", (time, log, try_entry))
        self.con.commit()

    def get_auth_info(self, log, password):
        cur = self.con.cursor()
        cur.execute(f'SELECT post, full_name FROM worker WHERE login="{log}" and password="{password}"')
        data = cur.fetchall()
        cur.close()
        if data != []:
            return data
        else:
            return False

    def add_order(self, service, id_client, id_order, time_serv):
        now = datetime.now()
        times = now.strftime("%H:%M")
        date = now.strftime("%d.%m.20%y")
        id = 1
        try:
            cur = self.con.cursor()
            cur.execute("""INSERT INTO order1 VALUES (NULL,?,?,?,?,?,?,?,?)""", (id_order, date, times, id_client, service, "Новая", '', time_serv))
            self.con.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Auth()

    app.exec()

