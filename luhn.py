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
