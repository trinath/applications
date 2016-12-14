basedigits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def decimaltobase62(number, basedigits=basedigits):
    if (number == 0):
        return basedigits[0]
    string=''
    base = len(basedigits)
    while number:
        rem = number%base
        number = number/base
        string=basedigits[rem]+string
    return string

def base62todecimal(string, basedigits=basedigits):
    base = len(basedigits)
    stringsize = len(string)
    number = 0
    id = 0
    for char in string:
        power = (stringsize - (id + 1))
        number += basedigits.index(char) * (base ** power)
        id += 1
    return number
