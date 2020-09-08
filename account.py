import random
random.seed(43)


class Account:
    def __init__(self):
        self.card_id = self._generate_card_id()
        self.pin = self._generate_pin()
        self.balance = 0

    def _generate_card_id(self):
        issuer_identification_number = 400000
        customer_account_number = str(random.randint(0, 999999999)).zfill(9)
        checksum = random.randint(0, 9)
        return f'{issuer_identification_number}{customer_account_number}{checksum}'

    def _generate_pin(self):
        return f'{random.randint(0, 9999)}'.zfill(4)


class AccountSupervisor:
    def __init__(self):
        self.accounts = {}

    def add_account(self):
        account = Account()
        if account.card_id in self.accounts.keys():
            return self.add_account()
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
