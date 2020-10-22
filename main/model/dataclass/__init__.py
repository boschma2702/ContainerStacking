from typing import Tuple

Container = Tuple[int, int, int]
StackLocation = Tuple[int, int]
StackTierLocation = Tuple[int, int, int]

def tuple_short_replace(tup, index, value):
    return tup[:index] + (value,) + tup[index+1:]


def tuple_long_replace(tup, index, value):
    lst = list(tup)
    lst[index] = value
    return tuple(lst)
