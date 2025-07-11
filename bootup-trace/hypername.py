#!/usr/bin/python3

import getopt
import sys
import os
import babeltrace.reader
from queue import *
HELP = "Usage: python hyperview.py path/to/trace --cpuid <CPU_ID> --pid <CPU>"
USERSPACE_HYPERCALL_NR = 2000
KERNELSPACE_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001
KVM_HYPERCALL = "kvm_x86_hypercall"
HYPERGRAPH_HOST = "hypergraph_host"
KVM_ENTRY = "kvm_x86_entry"
KVM_EXIT = "kvm_x86_entry"


def ns_to_us(timestamp):
    return (timestamp/float(1000))

def format_value(field_type, value):
    if field_type == 1:
        return int(value)
    elif field_type == 2:
        return float(value)
    elif field_type == 8:
        return [x for x in value]
    else:
        return str(value)

class Process:
    def __init__(self, filepath):
        self.filepath = filepath
        self.mappings = dict()
        with open(filepath) as f:
            lines = f.readlines()
            for line in lines:
                try:
                    values = line.strip().split(' ')
                    if not values[0] or not values[0].isdigit():
                        continue
                    pid = values[0]
                    pid = int(pid)
                    function_name = values[1] if len(values) <= 2 else values[2]
                    self.mappings[pid] = function_name.rstrip()
                except Exception as ex:
                    print(ex)

    def get_name(self, ip):
        if ip in self.mappings:
            return self.mappings[ip]
        return ""

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
                    ip = int(ip, 16)
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
        #     symbol = self.bst_lookup(ip, 0, len(self.bst) - 1)
        #     mapping = self.mappings[symbol]
        #     return mapping
        return ip


class HashTable:
    def __init__(self, file_path):
        self.file_path = file_path
        self.mappings = dict()
        with open(file_path) as f:
            lines = f.readlines()
            for line in lines:
                try:
                    values = line.strip().split(' ')
                    if not values[0]:
                        continue
                    ip = values[0]
                    ip = int(ip, 16)
                    function_name = values[1].strip() if len(values) <= 2 else values[2]
                    hash_code = self.string_hash(function_name)
                    if hash_code not in self.mappings:
                        self.mappings[hash_code] = [function_name]
                    elif function_name not in self.mappings[hash_code]:
                        self.mappings[hash_code].append(function_name)
                        print("function clashes %d, %s" % (hash_code, self.mappings[hash_code]))
                except Exception as ex:
                    print(ex)

    def string_hash(self, name):
        index = 0
        p = name[index]
        x = ord(p) << 7
        length = len(name) - 1
        while length >= 0:
            p = name[index]
            x = ((1000003 * x) ^ ord(p)) % 2 ** 64
            index += 1
            length -= 1

        x = (x ^ len(name)) % 2 ** 64
        if x == -1:
            x = -2
        return x

    def get_name(self, hash_code):
        if hash_code in self.mappings:
            values = self.mappings[hash_code]
            return values[0]
        return None


class Stack:
    def __init__(self):
        self.items = []
    def __str__(self):
        return ';'.join(self.items)
    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


def main(argv):
    path = ""

    kernel_symbols_path = os.path.join("./logs", "kallsyms.map")
    
    try:
        path = argv[0]
        if len(argv) > 0:
            kernel_symbols_path = argv[1]
    except Exception as ex:
        if not path:
            raise TypeError(HELP)

    # Create TraceCollection and add trace:
    # hash_table = HashTable(kernel_symbols_path)
    kernel_symbols = Symbols(kernel_symbols_path)
    process_list = Process(os.path.join("./logs", "process.txt"))

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")
    next_pid = 1
    for event in traces.events:
        if event.name != KVM_HYPERCALL and event.name != HYPERGRAPH_HOST:
            continue

        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        timestamp = event.timestamp
        nr = fields['nr']
        cpu_id = event['cpu_id']

        is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
        if is_sched_switch:
            prev_pid = fields['a0']
            prev_tgid = fields['a1']
            next_pid = fields['a2']
            next_tgid = fields['a3']

        else:
            function_address = fields['a0']
            is_entry = fields['a1'] == 0
            hash_code = fields["a2"]
            depth = fields["a3"]
            function_name = kernel_symbols.get_name(function_address)

            duration = fields["a2"]
            print("%s\t %s\t %s\t %s\t %s" % (str(function_name).rjust(50),
                                                   duration,
                                                   depth,
                                                   next_pid,
                                                   timestamp
                                                   )
                      )

if __name__ == "__main__":
    print("%s\t dur\t depth\t pid\t exit_time" % "function_name".rjust(50))
    try:
        main(sys.argv[1:])
    except Exception as ex:
        raise ex

