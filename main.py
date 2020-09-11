from bank import BankSystem
from database import Database


if __name__ == '__main__':
    bank_system = BankSystem(Database('card.s3db'))

    accounts = bank_system.get_accounts()
    for account in accounts:
        print(account)

    bank_system.main_loop()
