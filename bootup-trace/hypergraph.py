#!/usr/bin/python3

import getopt
import sys
import os
import babeltrace.reader

function_entry_map = dict()
HELP = "Usage: python hypergraph.py path/to/trace --cpuid <CPU_ID> --pid <CPU>"
USERSPACE_HYPERCALL_NR = 2000
KERNELSPACE_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001
KVM_HYPERCALL = "kvm_x86_hypercall"
KVM_ENTRY = "kvm_x86_entry"
KVM_EXIT = "kvm_x86_entry"

HEADER = """tracer: hypergraph

CPU  TASK/PID      DURATION      Depth         FUNCTION CALLS
 |    |    |         |   |         |           |   |   |   |"""
# tracer: function_graph
#
# CPU  TASK/PID         DURATION     Depth         FUNCTION CALLS
# |     |    |           |   |         |           |   |   |   |
#  7)   bash-21261   |   0.111 us    |  d=1  |  mutex_unlock();
#
#  5)   <->-0        | 0.674 us      | d=1  |

def ns_to_us(timestamp):
    return (timestamp/float(1000))

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


def main(argv):
    path = "/home/abder/lttng-traces/bootup-tracing-20170503-193327"
    input_word = ""
    input_cpuid = ""
    input_pid = ""
    data_pr_cpu = {0: {
        'prev_pid': 0, 'pid': 0, 'prev_task': '-', 'task': '-', 'prev_timestamp': 0, 'prev_function_name': ""
    }}
    try:
        path = argv[0]
        if len(argv) > 0:
            word = argv[1]
    except Exception as ex:
        if not path:
            raise TypeError(HELP)

    try:
        opts, args = getopt.getopt(argv, "h", ['cpuid=', 'pid='])
    except getopt.GetoptError:
        raise TypeError(HELP)

    for opt, arg in opts:
        if opt == '-h':
            raise TypeError(HELP)
        if opt == '--cpuid':
            input_cpuid = arg
        if opt == '--pid':
            input_pid = arg

    # Create TraceCollection and add trace:
    kernel_symbols = Symbols(os.path.join(path, "mapping/symbols.txt"))
    process_list = Process(os.path.join(path, "mapping/process.txt"))

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    print(HEADER)
    for event in traces.events:
        # if event.name != KVM_EXIT:

        if event.name != KVM_HYPERCALL:
            continue

        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        timestamp = event.timestamp

        nr = fields['nr']
        cpu_id = event['cpu_id']
        if cpu_id not in data_pr_cpu:
            data_pr_cpu[cpu_id] = {
                'prev_pid': 0, 'pid': 1, 'prev_task': '-', 'task': '-', 'prev_timestamp': 0, 'prev_function_name': ""
            }
        is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
        if is_sched_switch:
            prev_pid = fields['a0']
            prev_tgid = fields['a1']
            next_pid = fields['a2']
            next_tgid = fields['a3']

            data_pr_cpu[cpu_id]['prev_pid'] = prev_pid
            data_pr_cpu[cpu_id]['pid'] = next_pid
            data_pr_cpu[cpu_id]['prev_task'] = process_list.get_name(prev_pid)
            data_pr_cpu[cpu_id]['task'] = process_list.get_name(next_pid)
            print("".join(['-'] * 200))
            print("sched_switch on CPU %s  |  pid:%s->%s, tid:%s->%s" % (cpu_id, prev_pid, next_pid, prev_tgid, next_tgid))
            print("".join(['-'] * 200))
        else:
            # if show_pid != data_pr_cpu[cpu_id]['pid']:
            #     continue
            is_kernelspace = (nr == KERNELSPACE_HYPERCALL_NR)
            function_address = fields['a0']
            is_entry = fields['a1'] == 0
            is_irq = fields["a2"]
            depth = fields["a3"]
            function_name = function_address
            function_name = kernel_symbols.get_name(function_address)
            if function_name is None:
                continue
            # if (input_word != "" and input_word in function_name) or \
            #     str(cpu_id) == input_cpuid or \
            #                 input_pid != "" and str(data_pr_cpu[cpu_id]['pid']) == input_pid:
            if is_entry:
                data_pr_cpu[cpu_id]['entry_timestamp'] = timestamp
                data_pr_cpu[cpu_id]['entry_function_name'] = function_name

            elapsed_time = "" if is_entry else (str(ns_to_us(timestamp - data_pr_cpu[cpu_id]['entry_timestamp'])) + " us" if data_pr_cpu[cpu_id]['entry_timestamp'] > 0 else "" )
            # name = "{}() {{".format(function_name) if is_entry else "}} /* {} */".format(function_name)
            # name = "%s() { [%s-%s]" % (function_name, function_address, hex(function_address)) if is_entry else "}"
            name = "%s() { " % (function_name) if is_entry else "}"
            line = "%s)   <%s>-%s\t| %s\t| d=%s | %s%s" % \
                   (cpu_id, data_pr_cpu[cpu_id]['task'], data_pr_cpu[cpu_id]['pid'], elapsed_time.ljust(10), str(depth).ljust(2), "".join([' '*(cpu_id-1)*0])+"".join(['-'*depth]),name)
            print(line)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as ex:
        print(ex)
"""
do_one_initcall 3222275001
kallsyms_lookup 3223023465

"""
