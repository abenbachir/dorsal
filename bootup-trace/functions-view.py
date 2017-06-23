#!/usr/bin/python3

import getopt
import sys
import os
import babeltrace.reader
from queue import *
HELP = "Usage: python hyperview.py path/to/trace --cpuid <CPU_ID> --pid <CPU>"
USERSPACE_HYPERCALL_NR = 2000
KERNELSPACE_HYPERCALL_NR = 1000
KERNELSPACE_HYPERCALL_NR_2 = 1004
SCHED_SWITCH_HYPERCALL_NR = 1001
KVM_X86_HYPERCALL = "kvm_x86_hypercall"
KVM_HYPERCALL = "kvm_hypercall"
HYPERGRAPH_HOST = "hypergraph_host"
KVM_ENTRY = "kvm_x86_entry"
KVM_EXIT = "kvm_x86_exit"


def ns_to_us(timestamp):
    return (timestamp/float(1000))
def ns_to_ms(timestamp):
    return (timestamp/float(1000000))
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
        else:  # loop for
            symbol = self.bst_lookup(ip, 0, len(self.bst) - 1)
            mapping = self.mappings[symbol]
            return mapping
        return ip


class HashTable:

    def __init__(self, file_path):
        self.file_path = file_path
        self.mappings = dict()
        with open(file_path) as f:
            lines = f.readlines()
            self.arch = 64 if len(lines[0].strip().split(' ')[0]) > 8 else 32

            for line in lines:
                try:
                    values = line.strip().split(' ')
                    if not values[0]:
                        continue
                    ip = values[0]
                    ip = int(ip, 16)

                    function_name = values[1].strip() if len(values) <= 2 else values[2]
                    function_name = function_name.replace('\t', ' ')
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
            x = ((1000003 * x) ^ ord(p)) % 2 ** self.arch
            index += 1
            length -= 1

        x = (x ^ len(name)) % 2 ** self.arch
        if x == -1:
            x = -2
        return x

    def get_name(self, hash_code):
        if hash_code in self.mappings:
            values = self.mappings[hash_code]
            return values[0]
        return None


def main(argv):
    path = "/home/abder/ciena-trace-5/"
    kernel_symbols_path = "/home/abder/ciena-trace-5/mapping/kallsyms-x86.map"
    
    try:
        path = argv[0]
        if len(argv) > 0:
            kernel_symbols_path = argv[1]
    except Exception as ex:
        if not path:
            raise TypeError(HELP)

    # Create TraceCollection and add trace:
    hash_table = HashTable(kernel_symbols_path)
    kernel_symbols = Symbols(kernel_symbols_path)
    process_list = Process(os.path.join("./logs", "process.txt"))

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")
    next_pid = 1
    start_timestamp = 0
    for event in traces.events:
        if event.name != KVM_HYPERCALL and event.name != KVM_X86_HYPERCALL and event.name != HYPERGRAPH_HOST:
            continue

        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        timestamp = event.timestamp
        if start_timestamp == 0:
            start_timestamp = timestamp
        nr = fields['nr']
        cpu_id = event['cpu_id']

        is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
        is_kernelspace = (nr == KERNELSPACE_HYPERCALL_NR or nr == KERNELSPACE_HYPERCALL_NR_2)
        if is_sched_switch:
            prev_pid = fields['a0']
            prev_tgid = fields['a1']
            next_pid = fields['a2']
            next_tgid = fields['a3']
        elif is_kernelspace:
            function_ip = fields['a0']
            parent_ip = fields['a1']
            function_hash_code = fields["a2"]
            parent_hash_code = fields["a3"]
            function_name = kernel_symbols.get_name(function_ip)
            parent_name = kernel_symbols.get_name(parent_ip)

            function_name_from_hash = hash_table.get_name(function_hash_code)
            parent_name_from_hash = hash_table.get_name(parent_hash_code)

            if function_name.lower() != function_name_from_hash.lower():
                print("\nOops (current) : ip=%s, from_kallsyms=%s, from_hash=%s\n" % (function_ip, function_name,
                                                                        function_name_from_hash))
            if parent_name.lower() != parent_name_from_hash.lower():
                print("\nOops (parent) : ip=%s, from_kallsyms=%s, from_hash=%s\n" % (parent_ip, parent_name,
                                                                        parent_name_from_hash))
            duration = ns_to_ms(timestamp - start_timestamp)
            print("(%s) %s ms\t%s <-%s" % (cpu_id, duration, function_name, parent_name))

if __name__ == "__main__":
    print("CPU  |  function <- parent")

    main(sys.argv[1:])


