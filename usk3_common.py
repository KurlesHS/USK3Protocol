# coding=utf-8
__author__ = 'SVS'


def get_bytearray_from_number(number, array_size):
    return bytearray([(number >> (8 * i) & 0xff) for i in range(array_size)])


def get_number_from_bytearray(array):
    ret_val = 0
    for i, b in enumerate(array):
        ret_val |= b << (i * 8)
    return ret_val
