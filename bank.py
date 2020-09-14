from utils import singleton
from account import AccountSupervisor
from luhn import Luhn


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
