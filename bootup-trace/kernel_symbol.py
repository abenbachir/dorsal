#!/usr/bin/env python

import sys
import os

bst = []
mappings = dict()


def bst_lookup(bst, value, start, end):
    if end - start <= 1:
        return bst[start]

    mid = (end+start)/2
    middle_value = bst[mid]

    if value < middle_value :
        return bst_lookup(bst, value, start, mid)
    elif value > middle_value:
        return bst_lookup(bst, value, mid, end)
    elif middle_value == value:
        return value


def init_symbols():
    with open("./symbols.txt") as f:
        lines = f.readlines()
        for line in lines:
            values = line.split(' ')
            ip = int('0x' + values[0], 16)
            mode = values[1]
            function_name = values[2]
            # binarySearchTree[ip] = function_name
            bst.append(ip)
            mappings[ip] = function_name.rstrip()


def get_symbol_name(instruction_pointer):
    # only init the binary tree the first time
    if len(bst) == 0:
        init_symbols()

    if instruction_pointer in mappings:
        return mappings[instruction_pointer]
    else: # loop for
        return mappings[bst_lookup(bst, instruction_pointer, 0, len(bst) - 1)]



