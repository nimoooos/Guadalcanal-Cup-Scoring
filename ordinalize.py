def num_to_ordinal(number):
    last_digit = number % 10
    is_teen = False
    if 11 >= number % 100 >= 19:
        is_teen = True

    if is_teen or last_digit >= 4: return str(number + "th")
    if last_digit == 1: return str(number + "st")
    if last_digit == 2: return str(number + "nd")
    if last_digit == 3: return str(number + "rd")

