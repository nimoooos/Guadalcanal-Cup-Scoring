def num_to_ordinal(number):
    """
    Convert number to their ordinal value for placement purposes.
    Functions improperly if number>100, and will return "101th", "102th", etc.
    """
    last_digit = number % 10
    if number == 1: return str("🥇")
    if number == 2: return str("🥈")
    if number == 3: return str("🥉")

    if number <= 20: return str(number) + "th"

    if last_digit == 1: return str(number) + "st"
    if last_digit == 2: return str(number) + "nd"
    if last_digit == 3: return str(number) + "rd"
    else: return str(number) + "th"


def random_user_code():
    import random
    import string

    x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return x
