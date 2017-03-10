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
                try:
                    values = line.strip().split(' ')
                    if not values[0]:
                        continue
                    ip = values[0]
                    is_hex = len(ip) == 16 or 'f' in ip
                    ip = int('0x' + ip, 16) if is_hex else int(ip)
                    function_name = values[1] if len(values) <= 2 else values[2]
                    # binarySearchTree[ip] = function_name
                    self.bst.append(ip)
                    self.mappings[ip] = function_name.rstrip()
                except Exception as ex:
                    print(ex)

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

    def get_name(self, ip):
        if ip in self.mappings:
            return self.mappings[ip]
        # else:  # loop for
            # symbol = self.bst_lookup(ip, 0, len(self.bst) - 1)
            # mapping = self.mappings[symbol]
            # return mapping
        return ip
