#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from symbols import Symbols

function_entry_map = dict()
HELP = "Usage: python irq_hunter.py path/to/trace"
CATEGORY = "LTTng"
overheads = dict()
USERSPACE_HYPERCALL_NR = 2000
KERNELSPACE_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001

level_calls = {}

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



def main(argv):
    output = None
    start_recording = 0
    path = "/home/abder/lttng-traces/bootup-tracing-20170228-110344"
    word = ""
    cpuid = ""
    try:
        path = argv[0]
        if len(argv) > 0:
            word = argv[1]
    except:
        if not path:
            raise TypeError(HELP)

    try:
        opts, args = getopt.getopt(argv[1:], "hs:p:")
    except getopt.GetoptError:
        raise TypeError(HELP)
    count = 0
    max_count = 5000
    for opt, arg in opts:
        if opt == '-h':
            raise TypeError(HELP)
        if opt == '--cpuid':
            cpuid = arg

    # Create TraceCollection and add trace:
    kernel_symbols = Symbols("./logs/symbols.txt")
    process_list = Symbols("./logs/process.txt")

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    trace_events = []
    prev_timestamp = 0
    prev_process_name = ""
    next_process_name = ""
    for event in traces.events:
        # if count > max_count:
        #     break
        if event.name != "kvm_x86_hypercall":
            continue

        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        nr = fields['nr']
        timestamp = event.timestamp
        cpu_id = event['cpu_id']
        is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
        if is_sched_switch:
            prev_pid = fields['a0']
            prev_tgid = fields['a1']
            next_pid = fields['a2']
            next_tgid = fields['a3']

            prev_process_name = process_list.get_name(prev_pid)
            next_process_name = process_list.get_name(next_pid)
            print("".join(['-'] * 100))
            print("sched_switch  |  pid:{}->{}, tgid:{}->{}".format(prev_pid, next_pid, prev_tgid, next_tgid))
            print("".join(['-'] * 100))
        else:
            is_kernelspace = (nr == KERNELSPACE_HYPERCALL_NR)
            function_address = fields['a0']
            is_entry = fields['a1'] == 0
            is_irq = fields["a2"]
            depth = fields["a3"]
            function_name = kernel_symbols.get_name(function_address)
            # if not is_entry:
            #     continue

            if word is "" or word in function_name or cpu_id is cpuid:
                if is_entry:
                    count += 1
                count_display = count if is_entry else ""
                elapsed_time = (timestamp - prev_timestamp)/100 if prev_timestamp > 0 else 0
                prev_timestamp = timestamp
                name = "{}() {{".format(function_name) if is_entry else "}} /* {} */".format(function_name)
                # name = "{}() {{".format(function_name) if is_entry else "}"
                print("{}\t\t{}) +{} us\t\t [{}] | d={} | {} {}".format(count_display, cpu_id, elapsed_time, next_process_name, depth, "".join(['  ']*depth), name))


if __name__ == "__main__":
    main(sys.argv[1:])

