#!/usr/bin/python3

import os
import babeltrace.writer as btw
import babeltrace.reader
import multiprocessing

syscall_list_filepath = "/home/abder/utils/hypertracing/script/syscall_32.tbl"
HELP = "Usage: python babeltrace_json.py path/to/directory -o <outputfile>"
COMM_LENGTH = 16
KERNEL_MODE = "kernel"
USER_MODE = "ust"
CATEGORY = "LTTng"
CONFIG_ARCH_HYPERCALL_NR = 0
BOOTLEVEL_HYPERCALL_NR = 3000
USERSPACE_HYPERCALL_NR = 2000
FUNCTION_TRACING_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001
SCHED_WAKING_HYPERCALL_NR = 1002
SCHED_WAKEUP_HYPERCALL_NR = 1003
SCHED_WAKEUP_NEW_HYPERCALL_NR = 1004
SCHED_PROCESS_FORK_HYPERCALL_NR = 1005
SCHED_PROCESS_FREE_HYPERCALL_NR = 1006
SCHED_PROCESS_EXIT_HYPERCALL_NR = 1007

SYS_ENTRY_HYPERCALL_NR = 1100
SYS_EXIT_HYPERCALL_NR = 1101
SOFTIRQ_RAISE_HYPERCALL_NR = 1102
SOFTIRQ_ENTRY_HYPERCALL_NR = 1103
SOFTIRQ_EXIT_HYPERCALL_NR = 1104
IRQ_HANDLER_ENTRY_HYPERCALL_NR = 1105
IRQ_HANDLER_EXIT_HYPERCALL_NR = 1106

HRTIMER_INIT_HYPERCALL_NR = 1107
HRTIMER_START_HYPERCALL_NR = 1108
HRTIMER_EXPIRE_ENTRY_HYPERCALL_NR = 1109
HRTIMER_EXPIRE_EXIT_HYPERCALL_NR = 1110
HRTIMER_CANCEL_HYPERCALL_NR = 1111

VTID_FIELD_NAME = "vtid"
VPID_FIELD_NAME = "vpid"
ADDR_FIELD_NAME = "addr"
NAME_FIELD_NAME = "name"
PROCNAME_FIELD_NAME = "procname"
FUNC_ENTRY_EVENT_NAME = "func_entry"
FUNC_EXIT_EVENT_NAME = "func_exit"
SCHED_SWITCH_EVENT_NAME = "sched_switch"
SCHED_WAKING_EVENT_NAME = "sched_waking"
SCHED_WAKEUP_EVENT_NAME = "sched_wakeup"
SCHED_WAKEUP_NEW_EVENT_NAME = "sched_wakeup_new"
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
MARKER_EVENT_NAME = "marker"

HRTIMER_INIT_EVENT_NAME = "timer_hrtimer_init"
HRTIMER_START_EVENT_NAME = "timer_hrtimer_start"
HRTIMER_CANCEL_EVENT_NAME = "timer_hrtimer_cancel"
HRTIMER_EXPIRE_ENTRY_EVENT_NAME = "timer_hrtimer_expire_entry"
HRTIMER_EXPIRE_EXIT_EVENT_NAME = "timer_hrtimer_expire_exit"

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
event_types_map = {
    BOOTLEVEL_HYPERCALL_NR : MARKER_EVENT_NAME,
    SCHED_SWITCH_HYPERCALL_NR : SCHED_SWITCH_EVENT_NAME,
    SCHED_WAKING_HYPERCALL_NR : SCHED_WAKING_EVENT_NAME,
    SCHED_WAKEUP_HYPERCALL_NR : SCHED_WAKING_EVENT_NAME,
    SCHED_WAKEUP_NEW_HYPERCALL_NR : SCHED_WAKEUP_NEW_EVENT_NAME,

    SCHED_PROCESS_FORK_HYPERCALL_NR : SCHED_PROCESS_FORK_EVENT_NAME,
    SCHED_PROCESS_FREE_HYPERCALL_NR : SCHED_PROCESS_FREE_EVENT_NAME,
    SCHED_PROCESS_EXIT_HYPERCALL_NR : SCHED_PROCESS_EXIT_EVENT_NAME,

    SOFTIRQ_RAISE_HYPERCALL_NR: SOFTIRQ_RAISE_EVENT_NAME,
    SOFTIRQ_ENTRY_HYPERCALL_NR: SOFTIRQ_ENTRY_EVENT_NAME,
    SOFTIRQ_EXIT_HYPERCALL_NR: SOFTIRQ_EXIT_EVENT_NAME,
    IRQ_HANDLER_ENTRY_HYPERCALL_NR: IRQ_HANDLER_ENTRY_EVENT_NAME,
    IRQ_HANDLER_EXIT_HYPERCALL_NR: IRQ_HANDLER_EXIT_EVENT_NAME,
}


# create global fields
int8_type = btw.IntegerFieldDeclaration(8)
int8_type.signed = 1
int8_type.encoding = babeltrace.common.CTFStringEncoding.UTF8
int8_type.alignment = 8
array_type = btw.ArrayFieldDeclaration(int8_type, COMM_LENGTH)

string_type = btw.StringFieldDeclaration()
string_type.encoding = babeltrace.common.CTFStringEncoding.UTF8

int32_type = btw.IntegerFieldDeclaration(32)
int32_type.signed = 1
int64_type = btw.IntegerFieldDeclaration(64)
int64_type.signed = 1
uint32_type = btw.IntegerFieldDeclaration(32)
uint32_type.signed = 0
uint32_type.alignment = 8
uint64_type = btw.IntegerFieldDeclaration(64)
uint64_type.signed = 0
uint64_type.alignment = 8
uint64_hex_type = btw.IntegerFieldDeclaration(64)
uint64_hex_type.signed = 0
uint64_hex_type.alignment = 8
uint64_hex_type.base = 16

cpu_count = multiprocessing.cpu_count()
process_list = {}
previous_bootlevel = None
arch = 64


def is_32b():
    global arch
    return arch == 32

def get_previous_bootlevel():
    return previous_bootlevel

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
    nr = fields['nr'] & 0xffff
    vcpu_id = fields['nr'] >> 16
    cpu_id = vcpu_id  #event['cpu_id']
    events = []
    if cpu_id not in l1_pr_cpu:
        l1_pr_cpu[cpu_id] = {
            'prev_pid': -1, 'pid': -1,'prev_tid': -1, 'tid': -1, 'prev_comm': '-', 'task': '-', 'func_entry_timestamp': 0,
            'func_entry_function_name': "", "stack_head": ""
        }
    is_bootlevel = (nr == BOOTLEVEL_HYPERCALL_NR)
    is_function_tracing = (nr == FUNCTION_TRACING_HYPERCALL_NR)
    is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
    is_sched_wakeup = (nr == SCHED_WAKING_HYPERCALL_NR or nr == SCHED_WAKEUP_HYPERCALL_NR or nr == SCHED_WAKEUP_NEW_HYPERCALL_NR)
    is_sched_process_free_or_exit = (nr == SCHED_PROCESS_EXIT_HYPERCALL_NR or nr == SCHED_PROCESS_FREE_HYPERCALL_NR)
    is_sched_process_fork = (nr == SCHED_PROCESS_FORK_HYPERCALL_NR)
    is_softirq = (nr == SOFTIRQ_ENTRY_HYPERCALL_NR or nr == SOFTIRQ_EXIT_HYPERCALL_NR or nr == SOFTIRQ_RAISE_HYPERCALL_NR)
    is_syscall = (nr == SYS_ENTRY_HYPERCALL_NR or nr == SYS_EXIT_HYPERCALL_NR)
    is_irq_handler_entry = (nr == IRQ_HANDLER_ENTRY_HYPERCALL_NR )
    is_irq_handler_exit = (nr == IRQ_HANDLER_EXIT_HYPERCALL_NR)
    is_hrtimer = (nr >= HRTIMER_INIT_HYPERCALL_NR and nr <= HRTIMER_EXPIRE_EXIT_HYPERCALL_NR)

    if nr == CONFIG_ARCH_HYPERCALL_NR:
        global arch
        arch = fields['a0']*8  # 64 bits or 32 bits
        print('arch %s bits' % arch)

    if is_bootlevel:
        global previous_bootlevel
        nr_level, is_sync = fields['a0'], fields['a1']
        label = "%s%s" % (initcall_types[nr_level], ('_sync' if is_sync else ''))

        print(label)
        if previous_bootlevel is not None:
            events.append({"type": event_types_map[nr], "payload": {
                'label': previous_bootlevel['label'],
                'category': previous_bootlevel['label'].replace('_sync',''),
                'start': previous_bootlevel['timestamp'],
                'end': timestamp-500
            }})

        if label == 'late_sync':
            events.append({"type": event_types_map[nr], "payload": {
                'label': label,
                'category': label.replace('_sync', ''),
                'start': timestamp,
                'end': timestamp + 100000
            }})
        previous_bootlevel = {'label':label, 'timestamp':timestamp}

    if is_sched_switch:
        prev_state, prev_prio, next_prio = 0, 0, 0
        if is_32b():
            prev_tid, next_tid = fields['a0'] >> 16, fields['a0'] & 0xffff
            prev_state = fields['a1'] >> 24
            next_comm = get_comm([fields['a1'] & 0xffffff, fields['a2'], fields['a3']])
        else:
            # prev_state | prev_prio | prev_tid
            prev_state, prev_prio, prev_tid = fields['a0'] >> 32 + 16, ((fields['a0'] >> 32) & 0xffff), fields['a0'] & 0xffffffff
            # next_state | next_prio | next_tid
            next_state, next_prio, next_tid = fields['a1'] >> 32 + 16, ((fields['a1'] >> 32) & 0xffff), fields['a1'] & 0xffffffff
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
        events.append({"type": event_types_map[nr], "payload": payload})
    if is_sched_wakeup:
        comm = get_comm([fields['a3']])
        payload = {'tid': fields['a0'], 'prio': fields['a1'], 'target_cpu': fields['a2'], 'comm': list(comm)}
        events.append({"type": event_types_map[nr], "payload": payload})
    if is_sched_process_fork:

        comm = process_list[fields['a0']] if fields['a0'] in process_list else ''
        payload = {
                'parent_tid': fields['a0'], 'parent_pid': fields['a1'], 'parent_comm': list(comm),
                'child_tid': fields['a2'], 'child_pid': fields['a3'], 'child_comm': list(comm)
        }
        events.append({"type": SCHED_PROCESS_FORK_EVENT_NAME, "payload": payload})
    if is_sched_process_free_or_exit:
        comm = get_comm([fields['a2'], fields['a3']])
        event_type = SCHED_PROCESS_FREE_EVENT_NAME if nr == SCHED_PROCESS_FREE_HYPERCALL_NR \
            else SCHED_PROCESS_EXIT_EVENT_NAME
        # prio = fields['a1']
        events.append({"type": event_type, "payload": {'tid': fields['a0'], 'prio': 0, 'comm': comm}})
    if is_softirq:
        events.append({"type": event_types_map[nr], "payload": {'vec': fields['a0']}})
    if is_irq_handler_entry:
        events.append({"type": event_types_map[nr], "payload": {'irq': fields['a0'], 'name': ''}})
    if is_irq_handler_exit:
        events.append({"type": event_types_map[nr], "payload": {'irq': fields['a0'], 'ret': fields['a1']}})
    if is_hrtimer:
        payload = { 'hrtimer': fields['a0'] }
        if nr == HRTIMER_START_HYPERCALL_NR:
            payload['function'] = fields['a1']
            payload['expires'] = fields['a2']
            payload['softexpires'] = fields['a3']
        if nr == HRTIMER_EXPIRE_ENTRY_HYPERCALL_NR:
            payload['now'] = fields['a1']
            payload['function'] = fields['a2']
        events.append({"type": event_types_map[nr], "payload": payload})
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

    return cpu_id, events


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


def babeltrace_create_event_class(event_name, fields):
    event_class = btw.EventClass(event_name)
    for name, type in fields.items():
        event_class.add_field(type, name)
    return event_class

def babeltrace_create_writer(stream_name, path, per_cpu_streams):
    writer = btw.Writer(os.path.join(path, stream_name))
    clock = btw.Clock('monotonic')
    writer.add_clock(clock)
    writer.add_environment_field("domain", stream_name.split('-')[1])
    if KERNEL_MODE in stream_name:
        writer.add_environment_field("tracer_name", "lttng-modules")
        writer.add_environment_field("tracer_major", 2)
        writer.add_environment_field("tracer_minor", 10)
    else:
        writer.add_environment_field("tracer_name", "lttng-ust")

    stream_class = btw.StreamClass('channel')
    stream_class.clock = clock

    packet_context_type = stream_class.packet_context_type
    packet_context_type.add_field(uint32_type, "cpu_id")
    stream_class.packet_context_type = packet_context_type

    event_classes = {}
    if KERNEL_MODE in stream_name:
        # Sched switch
        sched_switch_event_class = btw.EventClass(SCHED_SWITCH_EVENT_NAME)
        sched_switch_event_class.add_field(array_type, "prev_comm")
        sched_switch_event_class.add_field(int32_type, "prev_tid")
        sched_switch_event_class.add_field(int32_type, "prev_prio")
        sched_switch_event_class.add_field(int64_type, "prev_state")
        sched_switch_event_class.add_field(array_type, "next_comm")
        sched_switch_event_class.add_field(int32_type, "next_tid")
        sched_switch_event_class.add_field(int32_type, "next_prio")
        stream_class.add_event_class(sched_switch_event_class)
        event_classes[SCHED_SWITCH_EVENT_NAME] = sched_switch_event_class
        # sched waking
        sched_waking_event_class = btw.EventClass(SCHED_WAKING_EVENT_NAME)
        sched_waking_event_class.add_field(int32_type, "tid")
        sched_waking_event_class.add_field(int32_type, "prio")
        sched_waking_event_class.add_field(int32_type, "target_cpu")
        sched_waking_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_waking_event_class)
        event_classes[SCHED_WAKING_EVENT_NAME] = sched_waking_event_class
        # sched wakeup
        sched_wakeup_event_class = btw.EventClass(SCHED_WAKEUP_EVENT_NAME)
        sched_wakeup_event_class.add_field(int32_type, "tid")
        sched_wakeup_event_class.add_field(int32_type, "prio")
        sched_wakeup_event_class.add_field(int32_type, "target_cpu")
        sched_wakeup_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_wakeup_event_class)
        event_classes[SCHED_WAKEUP_EVENT_NAME] = sched_wakeup_event_class
        # sched wakeup_new
        sched_wakeup_new_event_class = btw.EventClass(SCHED_WAKEUP_NEW_EVENT_NAME)
        sched_wakeup_new_event_class.add_field(int32_type, "tid")
        sched_wakeup_new_event_class.add_field(int32_type, "prio")
        sched_wakeup_new_event_class.add_field(int32_type, "target_cpu")
        sched_wakeup_new_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_wakeup_new_event_class)
        event_classes[SCHED_WAKEUP_NEW_EVENT_NAME] = sched_wakeup_new_event_class
        # sched process fork
        sched_process_fork_event_class = btw.EventClass(SCHED_PROCESS_FORK_EVENT_NAME)
        sched_process_fork_event_class.add_field(array_type, "parent_comm")
        sched_process_fork_event_class.add_field(int32_type, "parent_tid")
        sched_process_fork_event_class.add_field(int32_type, "parent_pid")
        sched_process_fork_event_class.add_field(array_type, "child_comm")
        sched_process_fork_event_class.add_field(int32_type, "child_tid")
        sched_process_fork_event_class.add_field(int32_type, "child_pid")
        stream_class.add_event_class(sched_process_fork_event_class)
        event_classes[SCHED_PROCESS_FORK_EVENT_NAME] = sched_process_fork_event_class
        # sched process exit
        sched_process_exit_event_class = btw.EventClass(SCHED_PROCESS_EXIT_EVENT_NAME)
        sched_process_exit_event_class.add_field(int32_type, "tid")
        sched_process_exit_event_class.add_field(int32_type, "prio")
        sched_process_exit_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_process_exit_event_class)
        event_classes[SCHED_PROCESS_EXIT_EVENT_NAME] = sched_process_exit_event_class
        # sched process free
        sched_process_free_event_class = btw.EventClass(SCHED_PROCESS_FREE_EVENT_NAME)
        sched_process_free_event_class.add_field(int32_type, "tid")
        sched_process_free_event_class.add_field(int32_type, "prio")
        sched_process_free_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_process_free_event_class)
        event_classes[SCHED_PROCESS_FREE_EVENT_NAME] = sched_process_free_event_class
        # softirq raise
        softirq_raise_event_class = btw.EventClass(SOFTIRQ_RAISE_EVENT_NAME)
        softirq_raise_event_class.add_field(uint32_type, "vec")
        stream_class.add_event_class(softirq_raise_event_class)
        event_classes[SOFTIRQ_RAISE_EVENT_NAME] = softirq_raise_event_class
        # softirq entry
        softirq_entry_event_class = btw.EventClass(SOFTIRQ_ENTRY_EVENT_NAME)
        softirq_entry_event_class.add_field(uint32_type, "vec")
        stream_class.add_event_class(softirq_entry_event_class)
        event_classes[SOFTIRQ_ENTRY_EVENT_NAME] = softirq_entry_event_class
        # softirq exit
        softirq_exit_event_class = btw.EventClass(SOFTIRQ_EXIT_EVENT_NAME)
        softirq_exit_event_class.add_field(uint32_type, "vec")
        stream_class.add_event_class(softirq_exit_event_class)
        event_classes[SOFTIRQ_EXIT_EVENT_NAME] = softirq_exit_event_class
        # irq handler entry
        irq_handler_entry_event_class = btw.EventClass(IRQ_HANDLER_ENTRY_EVENT_NAME)
        irq_handler_entry_event_class.add_field(int32_type, "irq")
        irq_handler_entry_event_class.add_field(string_type, "name")
        stream_class.add_event_class(irq_handler_entry_event_class)
        event_classes[IRQ_HANDLER_ENTRY_EVENT_NAME] = irq_handler_entry_event_class
        # irq handler exit
        irq_handler_exit_event_class = btw.EventClass(IRQ_HANDLER_EXIT_EVENT_NAME)
        irq_handler_exit_event_class.add_field(int32_type, "irq")
        irq_handler_exit_event_class.add_field(int32_type, "ret")
        stream_class.add_event_class(irq_handler_exit_event_class)
        event_classes[IRQ_HANDLER_EXIT_EVENT_NAME] = irq_handler_exit_event_class

        events_fields = {
            # timer
            HRTIMER_INIT_EVENT_NAME: {'hrtimer': uint64_hex_type, 'clockid': int32_type, 'mode': int32_type},
            HRTIMER_START_EVENT_NAME: {'hrtimer': uint64_hex_type, 'function': uint64_hex_type, 'expires': int64_type, 'softexpires': int64_type},
            HRTIMER_CANCEL_EVENT_NAME: {'hrtimer': uint64_hex_type},
            HRTIMER_EXPIRE_ENTRY_EVENT_NAME: {'hrtimer': uint64_hex_type, 'function': uint64_hex_type, 'now': int64_type},
            HRTIMER_EXPIRE_EXIT_EVENT_NAME: {'hrtimer': uint64_hex_type},
        }
        for event_name, fields in events_fields.items():
            event_class = babeltrace_create_event_class(event_name, fields)
            stream_class.add_event_class(event_class)
            event_classes[event_name] = event_class

        # syscall event class
        print(os.path.basename(syscall_list_filepath))
        syscalls = set([x['name'] for x in load_syscalls(syscall_list_filepath).values()])
        for name in syscalls:
            sys_entry_event_class = btw.EventClass("syscall_entry_%s" % name)
            sys_exit_event_class = btw.EventClass("syscall_exit_%s" % name)
            sys_exit_event_class.add_field(uint64_type, "ret")
            stream_class.add_event_class(sys_entry_event_class)
            stream_class.add_event_class(sys_exit_event_class)
            event_classes["syscall_entry_%s" % name] = sys_entry_event_class
            event_classes["syscall_exit_%s" % name] = sys_exit_event_class

        # marker events
        marker_event_class = btw.EventClass(MARKER_EVENT_NAME)
        marker_event_class.add_field(int64_type, "start")
        marker_event_class.add_field(int64_type, "end")
        marker_event_class.add_field(string_type, "category")
        marker_event_class.add_field(string_type, "label")
        stream_class.add_event_class(marker_event_class)
        event_classes[MARKER_EVENT_NAME] = marker_event_class
    else:
        # add this field declaration to event class
        func_entry_event_class = btw.EventClass(FUNC_ENTRY_EVENT_NAME)
        func_entry_event_class.add_field(uint64_type, ADDR_FIELD_NAME)
        func_entry_event_class.add_field(uint32_type, VTID_FIELD_NAME)
        func_entry_event_class.add_field(uint32_type, VPID_FIELD_NAME)
        func_entry_event_class.add_field(string_type, PROCNAME_FIELD_NAME)
        stream_class.add_event_class(func_entry_event_class)
        event_classes[FUNC_ENTRY_EVENT_NAME] = func_entry_event_class

        func_exit_event_class = btw.EventClass(FUNC_EXIT_EVENT_NAME)
        func_exit_event_class.add_field(uint64_type, ADDR_FIELD_NAME)
        func_exit_event_class.add_field(int32_type, VTID_FIELD_NAME)
        func_exit_event_class.add_field(int32_type, VPID_FIELD_NAME)
        func_exit_event_class.add_field(string_type, PROCNAME_FIELD_NAME)
        stream_class.add_event_class(func_exit_event_class)
        event_classes[FUNC_EXIT_EVENT_NAME] = func_exit_event_class

    if stream_name not in per_cpu_streams:
        per_cpu_streams[stream_name] = []

    for i in range(0, cpu_count):
        stream = writer.create_stream(stream_class)
        stream.packet_context.field("cpu_id").value = i
        per_cpu_streams[stream_name].append(stream)

    return event_classes