import random
import string

def six_digit_code():
    secret = ''.join(random.choices(string.digits, k=6))
    return secret
