from sqlite3 import IntegrityError
import random
from functools import wraps
import sqlite3
import sys
from sqlite3 import Error


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


class Luhn:
    @staticmethod
    def check(digits):
        # extract checksum
        checksum = int(digits[-1])

        # multiple odd number by 2
        digits_list = [int(digit) * 2 if i % 2 == 0 else int(digit)
                       for i, digit in enumerate(digits[:-1])]

        # subtract 9 from digits greater than 9
        digits_list = [digit - 9 if digit >
                       9 else digit for digit in digits_list]

        # merge digits with checksum
        digits_list += [checksum]

        return True if sum(digits_list) % 10 == 0 else False


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
        return self.cursor.fetchone() is not None


class Account:
    def __init__(self, card_id, pin, balance):
        self.card_id = card_id
        self.pin = pin
        self.balance = balance


@singleton
class AccountGenerator:
    def generate_account(self):
        card_id = self._generate_card_id()
        pin = self._generate_pin()
        balance = 0
        return card_id, pin, balance

    def _generate_card_id(self):
        bank_identification_number = '400000'
        account_identifier = str(random.randint(0, 999999999)).zfill(9)
        checksum = self._generate_checksum(
            bank_identification_number, account_identifier)
        return f'{bank_identification_number}{account_identifier}{checksum}'

    def _generate_checksum(self, bank_identification_number, account_identifier):
        digits = bank_identification_number + account_identifier
        digits_list = self._transform_digits(digits)
        return self._select_checksum(digits_list)

    @staticmethod
    def _transform_digits(digits):
        # multiple odd number by 2
        digits_list = [int(digit) * 2 if i % 2 == 0 else int(digit)
                       for i, digit in enumerate(digits)]

        # subtract 9 from digits greater than 9
        return [digit - 9 if digit > 9 else digit for digit in digits_list]

    @staticmethod
    def _select_checksum(digits_list):
        return (10 - sum(digits_list) % 10) % 10

    @staticmethod
    def _generate_pin():
        return f'{random.randint(0, 9999)}'.zfill(4)


@singleton
class AccountSupervisor:
    def __init__(self, database):
        self.database = database
        self.account_generator = AccountGenerator()

    def add_account(self):
        account_properties = self.account_generator.generate_account()
        card_id, pin, balance = account_properties

        try:
            self.database.add_account(card_id, pin, balance)
            return Account(*account_properties)
        except IntegrityError:
            return self.add_account()

    def get_account(self, card_id, pin):
        account_properties = self.database.get_account(card_id, pin)
        return Account(*account_properties) if account_properties else None

    def add_income(self, card_id, income):
        self.database.add_income(card_id, income)

    def close_account(self, account):
        self.database.close_account(account.card_id)

    def check_account(self, card_id):
        return self.database.check_account(card_id)


@singleton
class BankSystem:
    def __init__(self, database):
        self.login_state = LogInState(self)
        self.logout_state = LogOutState(self)
        self.state = self.logout_state

        self.account = None
        self.supervisor = AccountSupervisor(database)

    def show(self):
        self.state.show()

    def main_loop(self):
        while True:
            self.show()
            user_input = input()
            response = self.state.handle_input(user_input)
            if response == 'exit':
                return

    def set_state(self, state):
        self.state = self.login_state if state == 'login' else self.logout_state

    def get_state(self):
        return self.state

    def set_account(self, account):
        self.account = account

    def get_account(self):
        return self.account

    def get_card_id(self):
        return self.account.card_id

    def get_balance(self):
        if self.account:
            return self.account.balance

    def get_accounts(self):
        return self.supervisor.database.get_accounts()


@singleton
class LogOutState:
    def __init__(self, system):
        self.system = system

        self.methods = {
            '1': self._create_account,
            '2': self._log_into,
            '0': self._exit_app
        }

    @staticmethod
    def show():
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')

    def handle_input(self, user_input):
        if user_input not in self.methods.keys():
            raise KeyError

        return self.methods[user_input]()

    def _create_account(self):
        account = self.system.supervisor.add_account()
        print(('\nYour card has been created\n'
               'Your card number:\n'
               f'{account.card_id}\n'
               'Your card PIN:\n'
               f'{account.pin}\n'))

    def _get_account(self):
        print('\nEnter your card number:')
        card_id = input()

        print('Enter your PIN:')
        pin = input()

        return self.system.supervisor.get_account(card_id, pin)

    def _log_into(self):
        account = self._get_account()
        if not account:
            print('\nWrong card number or PIN!\n')
            return

        self.system.set_state('login')
        self.system.set_account(account)
        print('\nYou have successfully logged in!\n')

    @staticmethod
    def _exit_app():
        print('\nBye!')
        return 'exit'

    def __str__(self):
        return 'LogOut'


@singleton
class LogInState:
    def __init__(self, system):
        self.system = system

        self.methods = {
            '1': self._show_balance,
            '2': self._add_income,
            '3': self._do_transfer,
            '4': self._close_account,
            '5': self._log_out,
            '0': self._exit_app
        }

    @staticmethod
    def show():
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')

    def handle_input(self, user_input):
        if user_input not in self.methods.keys():
            raise KeyError

        return self.methods[user_input]()

    def _show_balance(self):
        print(f'\nBalance: {self.system.get_balance()}\n')

    def _add_income(self):
        print('\nEnter income:')
        income = int(input())

        self.system.account.balance += income
        self.system.supervisor.add_income(self.system.get_card_id(), income)
        print('Income was added!\n')

    def _do_transfer(self):
        print('\nTransfer')

        print('Enter card number:')
        card_id = input()
        if not self._check_card_id(card_id):
            return

        print('Enter how much money you want to transfer:')
        income = int(input())
        if self._transfer_money_if_possible(card_id, income):
            print('Success!\n')
        else:
            print('Not enough money!\n')

    def _check_card_id(self, card_id):
        if card_id == self.system.get_account().card_id:
            print("You can't transfer money to the same account!\n")
            return False

        if not Luhn.check(card_id):
            print('Probably you made a mistake in the card number. Please try again!\n')
            return False

        if not self.system.supervisor.check_account(card_id):
            print('Such a card does not exist.\n')
            return False

        return True

    def _transfer_money_if_possible(self, card_id, income):
        if income > self.system.get_balance():
            return False

        self.system.account.balance -= income
        self.system.supervisor.add_income(self.system.get_card_id(), -income)
        self.system.supervisor.add_income(card_id, income)
        return True

    def _close_account(self):
        self.system.supervisor.close_account(self.system.get_account())
        self.system.set_account(None)
        print('\nThe account has been closed!\n')

        self.system.set_state('logout')

    def _log_out(self):
        self.system.set_account(None)

        self.system.set_state('logout')
        print('\nYou have successfully logged out!\n')

    @staticmethod
    def _exit_app():
        print('\nBye!')
        return 'exit'

    def __str__(self):
        return 'LogIn'


if __name__ == '__main__':
    bank_system = BankSystem(Database('card.s3db'))
    bank_system.main_loop()
