#!/usr/bin/python3

import getopt
import sys
import os
import babeltrace.reader

HELP = "Usage: python get-bootup-time.py path/to/trace"
START_HYPERCALL_NR = 1002
END_HYPERCALL_NR = 1003
KERNELSPACE_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001
LEVEL_HYPERCALL_NR = 3000
KVM_X86_HYPERCALL = "kvm_x86_hypercall"
KVM_HYPERCALL = "kvm_hypercall"
HYPERGRAPH_HOST = "hypergraph_host"
KVM_ENTRY = "kvm_x86_entry"
KVM_EXIT = "kvm_x86_exit"

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
def main(argv):
    path = ""

    try:
        path = argv[0]
        if len(argv) > 0:
            kernel_symbols_path = argv[1]
    except Exception as ex:
        if not path:
            raise TypeError()

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    start_timestamp = 0
    end_timestamp = 0
    current_level = ""
    current_level_starttime = 0
    nr_events = 0
    for event in traces.events:
        if event.name != KVM_HYPERCALL and event.name != KVM_X86_HYPERCALL and event.name != HYPERGRAPH_HOST:
            continue

        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        timestamp = event.timestamp

        nr = fields['nr']
        if nr == START_HYPERCALL_NR:
            start_timestamp = timestamp
        elif nr == END_HYPERCALL_NR:
            end_timestamp = timestamp
        elif nr == LEVEL_HYPERCALL_NR:
            level_nr = fields['a0']
            is_sync = fields['a1'] == 1
            if current_level:
                print("%s = %s ms, %s events" % (current_level, ns_to_ms(timestamp-current_level_starttime), nr_events) )

            current_level = "".join([initcall_types.get(level_nr), "_sync" if is_sync else ""])
            current_level_starttime = timestamp
            nr_events = 0
        elif nr == SCHED_SWITCH_HYPERCALL_NR or nr == KERNELSPACE_HYPERCALL_NR:
            nr_events += 1

    print("Boot-up time = %s ms" % ns_to_ms(end_timestamp-start_timestamp))

if __name__ == "__main__":
    main(sys.argv[1:])