#!/usr/local/bin/python3
import sys
from database import Database


def my_isdigit(s):
    if isinstance(s, int):
        # if s is int, return s
        return s
    if isinstance(s, str) and s.isdigit():
        # if s is string and s is digit, return int(s)
        return abs(int(s))
    return 55


def generator(magic_num):

    if magic_num == '0':
        return "0 is not allowed"

    database = Database()
    fakelogs = ""
    while magic_num != 1:
        try:
            # get fake log from database
            results = database.get_fakelog(
                magic_num % 6 if isinstance(magic_num, int) else magic_num)
            # iterate over results
            for result in results:
                # check there has result and "string" value at index 1 starts with FAKE
                if result and result[1].startswith("FAKE"):
                    # append result to fakelogs
                    fakelogs += str(result) + '\n'
        except Exception as e:
            # if error, append error message to fakelogs
            fakelogs += str(e) + '\n'
        finally:
            # calculate next magic number
            magic_num = my_isdigit(magic_num)
            magic_num = 3 * magic_num + 1 if magic_num % 2 else magic_num // 2
    return fakelogs
