import random
random.seed(43)


class Account:
    def __init__(self):
        self.card_id = self._generate_card_id()
        self.pin = self._generate_pin()
        self.balance = 0

    def get_account_identifier(self):
        return self.card_id[7:-1]

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

    def _transform_digits(self, digits):
        # multiple odd number by 2
        digits_list = [int(digit) * 2 if i % 2 == 0 else int(digit)
                       for i, digit in enumerate(digits)]
        # subtract 9 from digits greater than 9
        return [digit - 9 if digit > 9 else digit for digit in digits_list]

    def _select_checksum(self, digits_list):
        return (10 - sum(digits_list) % 10) % 10

    def _generate_pin(self):
        return f'{random.randint(0, 9999)}'.zfill(4)


class AccountSupervisor:
    def __init__(self):
        self.account_identifiers = set()
        self.accounts = {}

    def add_account(self):
        account = Account()
        if account.get_account_identifier() in self.account_identifiers:
            return self.add_account()
        self.account_identifiers.add(account.get_account_identifier())
        self.accounts[account.card_id] = account
        return account

    def get_account(self, card_id, pin):
        if self._is_valid_account(card_id, pin):
            return self.accounts[card_id]
        return None

    def _is_valid_account(self, card_id, pin):
        return card_id in self.accounts and self.accounts[card_id].pin == pin


if __name__ == '__main__':
    supervisior = AccountSupervisor()

    supervisior.add_account()
    supervisior.add_account()
    supervisior.add_account()

    print(supervisior.accounts)

    for card_id, account in supervisior.accounts.items():
        print(account.card_id, account.pin, account.balance)

    # print(supervisior.get_account("4000000413947254"))
