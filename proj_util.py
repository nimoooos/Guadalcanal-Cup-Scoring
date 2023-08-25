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


def pivot_table(old_table):
    new_table = []
    num_rows = len(old_table)
    num_cols = len(old_table[0])

    # table validation
    for old_row in old_table:
        if len(old_row) != num_cols:
            print("Error: not every row has the same number of columns.")
            return []

    for index_new_row in range(num_cols):
        new_table.append([])
        for index_new_column in range(num_rows):
            new_table[index_new_row].append(old_table[index_new_column][index_new_row])

    return new_table