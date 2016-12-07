#!/usr/bin/env python

import sys
import os

class Symbols:

    def __init__(self, filepath):
        self.filepath = filepath
        self.bst = []
        self.mappings = dict()
        with open(filepath) as f:
            lines = f.readlines()
            for line in lines:
                values = line.split(' ')
                if not values[0]:
                    continue
                ip = int('0x' + values[0], 16)
                mode = values[1]
                function_name = values[2]
                # binarySearchTree[ip] = function_name
                self.bst.append(ip)
                self.mappings[ip] = function_name.rstrip()

    def bst_lookup(self, value, start, end):
        if end - start <= 1:
            return self.bst[start]

        mid = int((end+start)/2)
        middle_value = self.bst[mid]

        if value < middle_value :
            return self.bst_lookup(value, start, mid)
        elif value > middle_value:
            return self.bst_lookup(value, mid, end)
        elif middle_value == value:
            return value

    def get_symbol_name(self, instruction_pointer):
        if instruction_pointer in self.mappings:
            return self.mappings[instruction_pointer]
        else: # loop for
            symbol = self.bst_lookup(instruction_pointer, 0, len(self.bst) - 1)
            mapping = self.mappings[symbol]
            return mapping