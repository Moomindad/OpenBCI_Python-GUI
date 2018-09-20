#!/usr/bin/env python3.6
"""
:author Lars Oestreicher
"""
def str_to_intArray(s):
    """
    Converts an array of integers in string form ("[1,2,3,4,5,6]") into
    an array of integers.

    :param a string with a properly formatted array of integers:
    :return the corresponding array of proper integers:
    """
    a = []                           # An empty array to collect the result.
    for x in s[1:-1].split(','):     # A simple splitting of the string on ',' with the first and last
                                     # characters, '[' and ']' removed.
        a.append(int(x))             # append the next item converted to an integer.
    return(a)


