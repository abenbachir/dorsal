#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys

syscall_list_filepath = "/home/abder/utils/hypertracing/script/syscall_32.tbl"
HELP = "Usage: python babeltrace_json.py path/to/directory -o <outputfile>"
COMM_LENGTH = 16
CATEGORY = "LTTng"
CONFIG_ARCH_HYPERCALL_NR = 0
BOOTLEVEL_HYPERCALL_NR = 3000
USERSPACE_HYPERCALL_NR = 2000
FUNCTION_TRACING_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001
SCHED_PROCESS_FORK_HYPERCALL_NR = 1002
SCHED_PROCESS_FREE_HYPERCALL_NR = 1003
SCHED_PROCESS_EXIT_HYPERCALL_NR = 1004

SYS_ENTRY_HYPERCALL_NR = 1100
SYS_EXIT_HYPERCALL_NR = 1101
SOFTIRQ_RAISE_HYPERCALL_NR = 1102
SOFTIRQ_ENTRY_HYPERCALL_NR = 1103
SOFTIRQ_EXIT_HYPERCALL_NR = 1104
IRQ_HANDLER_ENTRY_HYPERCALL_NR = 1105
IRQ_HANDLER_EXIT_HYPERCALL_NR = 1106

VTID_FIELD_NAME = "vtid"
VPID_FIELD_NAME = "vpid"
ADDR_FIELD_NAME = "addr"
NAME_FIELD_NAME = "name"
PROCNAME_FIELD_NAME = "procname"
FUNC_ENTRY_EVENT_NAME = "func_entry"
FUNC_EXIT_EVENT_NAME = "func_exit"
SCHED_SWITCH_EVENT_NAME = "sched_switch"
SCHED_PROCESS_FORK_EVENT_NAME = "sched_process_fork"
SCHED_PROCESS_EXIT_EVENT_NAME = "sched_process_exit"
SCHED_PROCESS_FREE_EVENT_NAME = "sched_process_free"
SOFTIRQ_RAISE_EVENT_NAME = 'irq_softirq_raise'
SOFTIRQ_ENTRY_EVENT_NAME = 'irq_softirq_entry'
SOFTIRQ_EXIT_EVENT_NAME = 'irq_softirq_exit'

IRQ_HANDLER_ENTRY_EVENT_NAME = 'irq_handler_entry'
IRQ_HANDLER_EXIT_EVENT_NAME = 'irq_handler_exit'


KVM_X86_HYPERCALL_EVENT_NAME = "kvm_x86_hypercall"
KVM_HYPERCALL_EVENT_NAME = "kvm_hypercall"
HYPERGRAPH_HOST_EVENT_NAME = "hypergraph_host"
KVM_ENTRY_EVENT_NAME = "kvm_x86_entry"
KVM_EXIT_EVENT_NAME = "kvm_x86_exit"
INSTANT_BOOKMARK_EVENT_NAME = "bookmark"
BOOKMARK_START_EVENT_NAME = "bookmark_start"
BOOKMARK_END_EVENT_NAME = "bookmark_end"

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

irqs_event_type = {
    SOFTIRQ_RAISE_HYPERCALL_NR: SOFTIRQ_RAISE_EVENT_NAME,
    SOFTIRQ_ENTRY_HYPERCALL_NR: SOFTIRQ_ENTRY_EVENT_NAME,
    SOFTIRQ_EXIT_HYPERCALL_NR: SOFTIRQ_EXIT_EVENT_NAME,
    IRQ_HANDLER_ENTRY_HYPERCALL_NR: IRQ_HANDLER_ENTRY_EVENT_NAME,
    IRQ_HANDLER_EXIT_HYPERCALL_NR: IRQ_HANDLER_EXIT_EVENT_NAME,
}

process_list = {}
previous_bootlevel = ""
arch = 64

def is_32b():
    return arch == 32

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
    return name == KVM_HYPERCALL_EVENT_NAME or name == KVM_X86_HYPERCALL_EVENT_NAME \
           or name == HYPERGRAPH_HOST_EVENT_NAME


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
                    self.mappings[pid] = function_name.rstrip().replace('\t', ' ')
                except Exception as ex:
                    print(ex)

    def get_name(self, id):
        if id in self.mappings:
            return self.mappings[id]
        return None


class Symbols:
    def __init__(self, filepath):
        self.filepath = filepath
        self.bst = []
        self.mappings = dict()
        self.name_mappings = dict()
        if not os.path.exists(filepath):
            return
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


def load_syscalls(filepath):
    syscalls = {}
    with open(filepath) as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip().strip('\n')
            if line.startswith('#') or line == "":
                continue
            try:
                # 64 bits: <number> <abi> <name> <entry point>
                # 32 bits : <number> <abi> <name> <entry point> <compat entry point>
                values = list(filter(None, line.split('\t')))
                number, abi, name = values[0], values[1], values[2]
                syscalls[int(number)] = {'number': int(number), 'abi': abi, 'name': name}

            except Exception as ex:
                print(ex)
    return syscalls
syscalls = load_syscalls(syscall_list_filepath)

def get_comm(comms):
    import re
    thread_name = []
    for comm in comms:
        hexs = re.findall('..', hex(comm).replace('0x', ''))
        values = []
        for hex_val in hexs:
            thread_name.append(chr(int(hex_val, 16)))
        # values
        # thread_name.append("".join(values))
    thread_name.reverse()
    return "".join(thread_name)


def handle_l1_event(event):
    fields = get_fields(event)
    timestamp = event.timestamp
    nr = fields['nr']
    events = []
    cpu_id = event['cpu_id']
    if cpu_id not in l1_pr_cpu:
        l1_pr_cpu[cpu_id] = {
            'prev_pid': -1, 'pid': -1,'prev_tid': -1, 'tid': -1, 'prev_comm': '-', 'task': '-', 'func_entry_timestamp': 0,
            'func_entry_function_name': "", "stack_head": ""
        }
    is_bootlevel = (nr == CONFIG_ARCH_HYPERCALL_NR)
    is_bootlevel = (nr == BOOTLEVEL_HYPERCALL_NR)
    is_function_tracing = (nr == FUNCTION_TRACING_HYPERCALL_NR)
    is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
    is_sched_process_free_or_exit = (nr == SCHED_PROCESS_EXIT_HYPERCALL_NR or nr == SCHED_PROCESS_FREE_HYPERCALL_NR)
    is_sched_process_fork = (nr == SCHED_PROCESS_FORK_HYPERCALL_NR)
    is_softirq = (nr == SOFTIRQ_ENTRY_HYPERCALL_NR or nr == SOFTIRQ_EXIT_HYPERCALL_NR or nr == SOFTIRQ_RAISE_HYPERCALL_NR)
    is_syscall = (nr == SYS_ENTRY_HYPERCALL_NR or nr == SYS_EXIT_HYPERCALL_NR)
    is_irq_handler_entry = (nr == IRQ_HANDLER_ENTRY_HYPERCALL_NR )
    is_irq_handler_exit = (nr == IRQ_HANDLER_EXIT_HYPERCALL_NR)

    if nr == CONFIG_ARCH_HYPERCALL_NR:
        arch = fields['a0']*8
    if is_bootlevel:
        nr_level, is_sync = fields['a0'], fields['a1']
    #     name = "%s%s" % (initcall_types[nr_level], ('_sync' if is_sync else ''))
    #     previous_bootlevel = name
    #     events.append({"type": BOOKMARK_START_EVENT_NAME, "payload": {'name': name, 'color': nr_level}})
    #     if previous_bootlevel != "":
    #         events.append({"type": SCHED_SWITCH_EVENT_NAME, "payload": {'name': name, 'color': nr_level}})
    #         previous_bootlevel = name
    if is_sched_switch:
        prev_state, prev_prio, next_prio = 0, 0, 0
        if is_32b:
            prev_tid, next_tid = fields['a0'] >> 16, fields['a0'] & 0xffff
            next_comm = get_comm([fields['a1'], fields['a2'], fields['a3']])
        else:
            prev_tid, next_tid = fields['a0'] >> 16, fields['a0'] & 0xffff
            next_comm = get_comm([fields['a2'], fields['a3']])
        # prev_comm = l1_pr_cpu[cpu_id]['next_comm'] if 'next_comm' in l1_pr_cpu[cpu_id] else 'Unknown %s' % prev_tid
        process_list[next_tid] = next_comm
        prev_comm = process_list[prev_tid] if prev_tid in process_list else 'Unknown %s' % prev_tid

        l1_pr_cpu[cpu_id]['prev_tid'] = prev_tid
        l1_pr_cpu[cpu_id]['tid'] = next_tid
        l1_pr_cpu[cpu_id]['next_comm'] = next_comm
        l1_pr_cpu[cpu_id]['prev_comm'] = prev_comm
        payload = {'prev_tid': prev_tid, 'prev_prio': prev_prio, 'prev_state': prev_state, 'next_tid': next_tid,
                   'next_prio': next_prio, 'prev_comm': list(prev_comm), 'next_comm': list(next_comm)
        }
        events.append({"type": SCHED_SWITCH_EVENT_NAME, "payload": payload})
    if is_sched_process_fork:
        payload = {
                'parent_tid': fields['a0'], 'parent_pid': fields['a1'], 'parent_comm': list(process_list[fields['a0']]),
                'child_tid': fields['a2'], 'child_pid': fields['a3'], 'child_comm': list(process_list[fields['a0']])
        }
        events.append({"type": SCHED_PROCESS_FORK_EVENT_NAME, "payload": payload})
    if is_sched_process_free_or_exit:
        comm = get_comm([fields['a2'], fields['a3']])
        event_type = SCHED_PROCESS_FREE_EVENT_NAME if nr == SCHED_PROCESS_FREE_HYPERCALL_NR \
            else SCHED_PROCESS_EXIT_EVENT_NAME
        # prio = fields['a1']
        events.append({"type": event_type, "payload": {'tid': fields['a0'], 'prio': 0, 'comm': comm}})
    if is_softirq:
        events.append({"type": irqs_event_type[nr], "payload": {'vec': fields['a0']}})
    if is_irq_handler_entry:
        events.append({"type": irqs_event_type[nr], "payload": {'irq': fields['a0'], 'name': ''}})
    if is_irq_handler_exit:
        events.append({"type": irqs_event_type[nr], "payload": {'irq': fields['a0'], 'ret': fields['a1']}})
    if is_syscall:
        payload = {}
        syscall_nr = fields['a0']
        if syscall_nr in syscalls:
            entry_or_exit = 'entry' if nr == SYS_ENTRY_HYPERCALL_NR else 'exit'
            sys_type = 'syscall_%s_%s' % (entry_or_exit, syscalls[syscall_nr]['name'])
            if nr == SYS_EXIT_HYPERCALL_NR:
                payload = {'ret': fields['a1']}
            events.append({"type": sys_type, "payload": payload})
        else:
            print('syscall number not found %s' % syscall_nr)

    if is_function_tracing:
        addr = fields['a0']
        is_entry = fields['a1'] == 0
        hash_code = fields["a2"]
        depth = fields["a3"]
        function_name = addr
        procname = "Guest: Unknown"

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
        events.append(exit_obj)

    return events


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
    is_function_tracing = ("func_" in event.name)

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
        return {"type": event.name, "payload":fields}

    if is_function_tracing:
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
