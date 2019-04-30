import itertools

def is_a_positive_int(number):
    try:
        if isinstance(number, int):
            if number >= 0:
                return True
        number = float(number)
        decimal_part = str(number - int(number))[1:]
        if number >= 0 and float(decimal_part) == 0:
            return True
        return False
    except ValueError:
        return False

def less_than_universal_set(uni_set_size, set_size):
    if uni_set_size >= set_size:
        return True
    return False

def check_consistency(num_of_digits, data):
    a = ord('a')
    symbols = []

    for i in range(num_of_digits):
        symbols.append(chr(a + i))


    for i in range(len(symbols)):
        comb = itertools.combinations(symbols, i+1)
        # for combi in comb:
        #     print(combi)

