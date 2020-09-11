from utils import singleton
from sqlite3 import Error, IntegrityError
import random
random.seed(43)


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
            print('Integrity Error')
            return self.add_account()

    def get_account(self, card_id, pin):
        account_properties = self.database.get_account(card_id, pin)
        return Account(*account_properties) if account_properties else None
