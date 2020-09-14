import sqlite3
import sys
from sqlite3 import Error

from utils import singleton


@singleton
class Database:
    def __init__(self, database_file):
        self.conn = self._create_connection(database_file)
        self.cursor = self.conn.cursor()

        self._create_accounts_table()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    @staticmethod
    def _create_connection(database_file):
        try:
            return sqlite3.connect(database_file)
        except Error as e:
            print(e)
            sys.exit()

    def _create_accounts_table(self):
        sql_create_table = f""" CREATE TABLE IF NOT EXISTS card (
                                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                                       number TEXT UNIQUE,
                                       pin TEXT,
                                       balance INTEGER DEFAULT 0); """
        self.cursor.execute(sql_create_table)
        self.conn.commit()

    def add_account(self, number, pin, balance):
        sql_add_account = f""" INSERT INTO card (number, pin, balance)
                               VALUES ({number}, {pin}, {balance}); """
        self.cursor.execute(sql_add_account)
        self.conn.commit()

    def get_account(self, number, pin):
        sql_get_account = f""" SELECT number, pin, balance FROM card 
                               WHERE {number} = number AND {pin} = pin """
        self.cursor.execute(sql_get_account)
        account_properties = self.cursor.fetchone()
        return account_properties

    def add_income(self, number, income):
        sql_add_income = f""" UPDATE card 
                              SET balance = balance + {income}
                              WHERE {number} = number """
        self.cursor.execute(sql_add_income)
        self.conn.commit()

    def close_account(self, number):
        sql_close_account = f""" DELETE FROM card 
                                 WHERE {number} = number """
        self.cursor.execute(sql_close_account)
        self.conn.commit()

    def check_account(self, number):
        sql_check_account = f""" SELECT * FROM card 
                                 WHERE {number} = number """
        self.cursor.execute(sql_check_account)
        return self.cursor.fetchone() != None

    def get_accounts(self):
        sql_get_account = f""" SELECT * FROM card """
        self.cursor.execute(sql_get_account)
        accounts = self.cursor.fetchall()
        return accounts
