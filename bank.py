from account import Account, AccountGenerator, AccountSupervisor
from utils import singleton


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

    def get_accounts(self):
        return self.supervisor.database.get_accounts()

    def get_balance(self):
        if self.account:
            return self.account.balance


@singleton
class LogOutState:
    def __init__(self, system):
        self.system = system

    @staticmethod
    def show():
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')

    def handle_input(self, user_input):
        if user_input == '1':
            return self._create_account()

        if user_input == '2':
            return self._log_into()

        if user_input == '0':
            return self._exit_app()

        raise AttributeError

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
        self.system.account = account
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

    @staticmethod
    def show():
        print('1. Balance')
        print('2. Log out')
        print('0. Exit')

    def handle_input(self, user_input):
        if user_input == '1':
            return self._show_balance()

        if user_input == '2':
            return self._log_out()

        if user_input == '0':
            return self._exit_app()

        raise AttributeError

    def _show_balance(self):
        print(f'\nBalance: {self.system.get_balance()}\n')

    def _log_out(self):
        self.system.set_state('logout')
        self.system.account = None
        print('\nYou have successfully logged out!\n')

    @staticmethod
    def _exit_app():
        print('\nBye!')
        return 'exit'

    def __str__(self):
        return 'LogIn'
