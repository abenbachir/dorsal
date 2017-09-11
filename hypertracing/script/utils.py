#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys


HELP = "Usage: python babeltrace_json.py path/to/directory -o <outputfile>"
CATEGORY = "LTTng"
USERSPACE_HYPERCALL_NR = 2000
LEVEL_HYPERCALL_NR = 3000
KERNELSPACE_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001
KVM_X86_HYPERCALL = "kvm_x86_hypercall"
KVM_HYPERCALL = "kvm_hypercall"
HYPERGRAPH_HOST = "hypergraph_host"
KVM_ENTRY = "kvm_x86_entry"
KVM_EXIT = "kvm_x86_exit"
initcall_types = {
    0: 'early',
    1: 'pure',
    2: 'core',
    3: 'postcore',
    4: 'arch',
    5: 'subsys',
    6: 'fs',
    7: 'rootfs',
    8: 'device',
    9: 'late',
    10: 'console',
    11: 'security'
}


def ns_to_us(timestamp):
    return timestamp/float(1000)


def ns_to_ms(timestamp):
    return timestamp/float(1000000)


def format_value(field_type, value):
    if field_type == 1:
        return int(value)
    elif field_type == 2:
        return float(value)
    elif field_type == 8:
        return [x for x in value]
    else:
        return str(value)


def get_fields(event):
    fields = dict()
    for k, v in event.items():
        field_type = event._field(k).type
        fields[k] = format_value(field_type, v)
    return fields

def is_hypercall_event(name):
    return name == KVM_HYPERCALL or name == KVM_X86_HYPERCALL or name == HYPERGRAPH_HOST

class Process:
    def __init__(self, filepath):
        self.filepath = filepath
        self.mappings = dict()
        if not os.path.exists(filepath):
            return
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
        self.name_mappings = dict()
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
                    self.mappings[ip] = function_name.rstrip().replace('\t', ' ')
                    self.name_mappings[function_name.rstrip().replace('\t', ' ')] = ip
                except Exception as ex:
                    print(ex)

    def get_addr(self, name):
        if name in self.name_mappings:
            return self.name_mappings[name]
        return None

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
            for line in lines:
                try:
                    values = line.strip().split(' ')
                    if not values[0]:
                        continue
                    ip = values[0]
                    ip = int(ip, 16)
                    function_name = values[1].strip() if len(values) <= 2 else values[2]
                    hash_code = self.string_hash(function_name)
                    function_name = function_name.rstrip().replace('\t', ' ')
                    if hash_code not in self.mappings:
                        self.mappings[hash_code] = [function_name]
                    elif function_name not in self.mappings[hash_code]:
                        self.mappings[hash_code].append(function_name)
                        print("function clashes %d, %s" % (hash_code, self.mappings[hash_code]))
                except Exception as ex:
                    print(ex)

    def string_hash(self, name, arch=64):
        index = 0
        p = name[index]
        x = ord(p) << 7
        length = len(name) - 1
        while length >= 0:
            p = name[index]
            x = ((1000003 * x) ^ ord(p)) % 2 ** arch
            index += 1
            length -= 1

        x = (x ^ len(name)) % 2 ** arch
        if x == -1:
            x = -2
        return x

    def get_name(self, hash_code):
        if hash_code in self.mappings:
            values = self.mappings[hash_code]
            return values[0]
        return None
l0_pr_cpu = {0: {
    'prev_tid': 0, 'tid': 1, 'prev_pid': 0, 'pid': 0, 'prev_task': '-', 'task': '-',
    'func_entry_timestamp': 0, 'func_entry_function_name': "", "stack_head":""
}}
l1_pr_cpu = {0: {
    'prev_tid': 0, 'tid': 1, 'prev_pid': 0, 'pid': 0, 'prev_task': '-', 'task': '-',
    'func_entry_timestamp': 0, 'func_entry_function_name': "", "stack_head":""
}}

l0_hash_dict = dict()
l1_hash_dict = dict()


class EventFunction:
    function_name = ""
    dur = 0
    guest_dur = 0
    is_leaf = False
    procname = ""
    def __init__(self, timestamp, address, hash_code, depth, pid, tid, cpu_id, virt_level):
        self.timestamp = timestamp
        self.function_name = address
        self.address = address
        self.hash_code = hash_code
        self.depth = depth
        self.pid = pid
        self.tid = tid
        self.cpu_id = cpu_id
        self.virt_level = virt_level

    def str(self):
        return "EntryExit %s %s %s" % (self.virt_level, self.address, self.hash_code)


class FunctionEntry(EventFunction):
    def __str__(self):
        return "Entry : %s" % self.str()


class FunctionExit(EventFunction):
    def __str__(self):
        return "Exit : %s" % self.str()

class FunctionExitOnly(EventFunction):
    calltime = 0
    def __str__(self):
        return "Exit : %s" % self.str()


def handle_l1_event(event):
    fields = get_fields(event)
    timestamp = event.timestamp

    nr = fields['nr']
    cpu_id = event['cpu_id']
    if cpu_id not in l1_pr_cpu:
        l1_pr_cpu[cpu_id] = {
            'prev_pid': 0, 'pid': 1,'prev_tid': 0, 'tid': 1, 'prev_task': '-', 'task': '-', 'func_entry_timestamp': 0,
            'func_entry_function_name': "", "stack_head": ""
        }
    is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
    is_kernelspace = (nr == KERNELSPACE_HYPERCALL_NR)

    if is_sched_switch:
        prev_pid = fields['a0']
        prev_tgid = fields['a1']
        next_pid = fields['a2']
        next_tgid = fields['a3']

        l1_pr_cpu[cpu_id]['prev_pid'] = prev_pid
        l1_pr_cpu[cpu_id]['pid'] = next_pid
        l1_pr_cpu[cpu_id]['prev_tid'] = prev_tgid
        l1_pr_cpu[cpu_id]['tid'] = next_tgid
        sched_fields = {timestamp, cpu_id, prev_pid, next_pid, prev_tgid, next_tgid}
        return None
        # return {"type": "sched_switch", "fields": sched_fields}

    if is_kernelspace:
        addr = fields['a0']
        is_entry = fields['a1'] == 0
        hash_code = fields["a2"]
        depth = fields["a3"]
        function_name = addr
        pid = fields['pid']
        tid = fields['tid']
        procname = "KVM Guest CPU%s" % (cpu_id) #"".join(fields['procname'])

        if is_entry:
            if addr not in l1_hash_dict:
                l1_hash_dict[addr] = hash_code
            l1_pr_cpu[cpu_id]['func_entry_timestamp'] = timestamp
            l1_pr_cpu[cpu_id]['func_entry_function_name'] = function_name
            l1_pr_cpu[cpu_id]['stack_head'] = function_name
            entry_obj = FunctionEntry(timestamp, addr, hash_code, depth,
                                 l1_pr_cpu[cpu_id]['pid'],
                                 l1_pr_cpu[cpu_id]['tid'],
                                 cpu_id,
                                 "L1")
            entry_obj.procname = procname
            return entry_obj
        is_leaf = not is_entry and l1_pr_cpu[cpu_id]['stack_head'] == function_name
        guest_dur = fields["a2"]
        dur = timestamp - l1_pr_cpu[cpu_id]['func_entry_timestamp']

        hash_code = l1_hash_dict[addr] if addr in l1_hash_dict else 0
        exit_obj = FunctionExit(timestamp, addr, hash_code, depth,
                      l1_pr_cpu[cpu_id]['pid'],
                      l1_pr_cpu[cpu_id]['tid'],
                      cpu_id,
                      "L1")
        exit_obj.dur = dur
        exit_obj.guest_dur = guest_dur
        exit_obj.is_leaf = is_leaf
        exit_obj.procname = procname
        return exit_obj
    return None

def handle_l0_event(event):
    fields = get_fields(event)
    timestamp = event.timestamp

    cpu_id = event['cpu_id']
    if cpu_id not in l0_pr_cpu:
        l0_pr_cpu[cpu_id] = {
            'prev_pid': 0, 'pid': 1,'prev_tid': 0, 'tid': 1, 'prev_task': '-', 'task': '-', 'func_entry_timestamp': 0,
            'func_entry_function_name': "", "stack_head": ""
        }
    is_sched_switch = (event.name == "sched_switch")
    is_kernelspace = ("func_" in event.name)

    if is_sched_switch:
        prev_pid = fields['prev_tid']
        prev_tgid = fields['prev_tid']
        next_pid = fields['next_tid']
        next_tgid = fields['next_tid']

        l0_pr_cpu[cpu_id]['prev_pid'] = prev_pid
        l0_pr_cpu[cpu_id]['pid'] = next_pid
        l0_pr_cpu[cpu_id]['prev_tid'] = prev_tgid
        l0_pr_cpu[cpu_id]['tid'] = next_tgid
        l0_pr_cpu[cpu_id]['prev_task'] = fields["prev_comm"]
        l0_pr_cpu[cpu_id]['task'] = fields["next_comm"]
        return {"type": event.name, "fields":fields}

    if is_kernelspace:
        # if show_pid != l0_pr_cpu[cpu_id]['pid']:
        #     continue
        pid = fields['pid']
        tid = fields['tid']
        procname = "".join(fields['procname'])
        addr = fields['ip']
        function_name = addr
        is_entry = event.name == "func_entry"
        is_exit = event.name == "func_exit"
        is_entry_exit = event.name == "func_entry_exit"

        depth = fields["depth"]

        if is_entry:
            hash_code = fields["hash"]
            if addr not in l1_hash_dict:
                l1_hash_dict[addr] = hash_code
            l0_pr_cpu[cpu_id]['func_entry_timestamp'] = timestamp
            l0_pr_cpu[cpu_id]['func_entry_function_name'] = function_name
            l0_pr_cpu[cpu_id]['stack_head'] = function_name
            entry_obj = FunctionEntry(timestamp, addr, hash_code, depth, pid, tid, cpu_id,"L0")
            entry_obj.procname = procname
            return entry_obj
        if is_exit:
            dur = fields["duration"]
            is_leaf = not is_entry and l0_pr_cpu[cpu_id]['stack_head'] == function_name
            # dur = timestamp - l0_pr_cpu[cpu_id]['func_entry_timestamp']

            hash_code = l1_hash_dict[addr] if addr in l1_hash_dict else 0
            exit_obj = FunctionExit(timestamp, addr, hash_code, depth, pid, tid, cpu_id, "L0")
            exit_obj.dur = dur
            exit_obj.guest_dur = dur
            exit_obj.is_leaf = is_leaf
            exit_obj.procname = procname
            return exit_obj
        if is_entry_exit:
            calltime = fields["calltime"]
            dur = calltime - timestamp
            is_leaf = not is_entry and l0_pr_cpu[cpu_id]['stack_head'] == function_name
            # dur = timestamp - l0_pr_cpu[cpu_id]['func_entry_timestamp']

            hash_code = l1_hash_dict[addr] if addr in l1_hash_dict else 0
            obj = FunctionExitOnly(timestamp, addr, hash_code, depth, pid, tid, cpu_id, "L0")
            obj.dur = dur
            obj.guest_dur = dur
            obj.is_leaf = is_leaf
            obj.procname = procname
            obj.calltime = calltime
            return obj
        return None

syscalls = ["sys_open"]