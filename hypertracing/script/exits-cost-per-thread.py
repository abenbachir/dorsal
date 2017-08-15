#!/usr/bin/python3

import getopt
import sys
import os
import operator
import babeltrace.reader


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
# see tools/arch/x86/include/uapi/asm/vmx.h
EXIT_REASONS = {
    0: "EXCEPTION_NMI",
    1: "EXTERNAL_INTERRUPT",
    2: "TRIPLE_FAULT",
    3: "INIT_SIGNAL",
    4: "SIPI",
    5: "IO_SMI",
    6: "OTHER_SMI",
    7: "PENDING_INTERRUPT",
    8: "NMI_WINDOW",
    9: "TASK_SWITCH",
    10: "CPUID",
    11: "GETSEC",
    12: "HLT",
    13: "INVD",
    14: "INVLPG",
    15: "RDPMC",
    16: "RDTSC",
    17: "RSM",
    18: "VMCALL",
    19: "VMCLEAR",
    20: "VMLAUNCH",
    21: "VMPTRLD",
    22: "VMPTRST",
    23: "VMREAD",
    24: "VMRESUME",
    25: "VMWRITE",
    26: "VMOFF",
    27: "VMON",
    28: "CR_ACCESS",
    29: "DR_ACCESS",
    30: "IO_INSTRUCTION",
    31: "MSR_READ",
    32: "MSR_WRITE",
    33: "INVALID_STATE",
    34: "MSR_LOAD_FAIL",
    36: "MWAIT_INSTRUCTION",
    37: "MONITOR_TRAP_FLAG",
    39: "MONITOR_INSTRUCTION",
    40: "PAUSE_INSTRUCTION",
    41: "MCE_DURING_VMENTRY",
    43: "TPR_BELOW_THRESHOLD",
    44: "APIC_ACCESS",
    45: "EOI_INDUCED",
    46: "ACCESS_GDTR_OR_IDTR",
    47: "ACCESS_LDTR_OR_TR",
    48: "EPT_VIOLATION",
    49: "EPT_MISCONFIG",
    50: "INVEPT",
    51: "RDTSCP",
    52: "PREEMPTION_TIMER",
    53: "INVVPID",
    54: "WBINVD",
    55: "XSETBV",
    56: "APIC_WRITE",
    58: "INVPCID",
    62: "PML_FULL",
    63: "XSAVES",
    64: "XRSTORS",
}

def main(argv):
    path = ""
    print_header = -1

    try:
        path = argv[0]
        if len(argv) > 1:
            print_header = int(argv[1])
    except Exception as ex:
        if not path:
            raise TypeError()

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")
    splits = path.split('-')
    layer = splits[2].upper()
    tracer = splits[4].capitalize()
    arg3 = splits[6]

    if print_header > 0:
        print("layer,tracer,maxprime,event,freq,total_event_cost,cost_per_event")

    threads = dict()
    current_tid = -1
    is_sched_switch = False
    count = 0
    exit_reason = -1
    for event in traces.events:
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        cpu_id = event['cpu_id']
        timestamp = event.timestamp

        # Handle hypercall (sched_switch)
        if event.name == "kvm_x86_hypercall":
            nr = fields['nr']
            if nr == 1002:
                next_pid = fields['a2']
                next_tgid = fields['a3']
                current_tid = '%s-%s' % (next_pid, next_tgid)
            if current_tid not in threads:
                threads[current_tid] = {
                    'kvm_events': {},
                    'kvm_exit_cost': {},
                    'kvm_exit_freq': {},
                    'exit_timestamp': 0,
                    'entry_timestamp': 0
                }
            continue

        if current_tid == -1:
            continue
        thread = threads[current_tid]

        if event.name == "kvm_x86_exit":
            thread['exit_timestamp'] = timestamp
            exit_reason = fields['exit_reason']

            if exit_reason not in thread['kvm_exit_freq']:
                thread['kvm_exit_freq'][exit_reason] = 0
                thread['kvm_exit_cost'][exit_reason] = 0
            # increment freq
            thread['kvm_exit_freq'][exit_reason] = thread['kvm_exit_freq'][exit_reason] + 1

        elif event.name == "kvm_x86_entry" and thread['exit_timestamp'] != 0:
            thread['entry_timestamp'] = timestamp
            duration = thread['entry_timestamp']-thread['exit_timestamp']
            thread['kvm_exit_cost'][exit_reason] = thread['kvm_exit_cost'][exit_reason] + duration
            thread['exit_timestamp'] = 0
            thread['entry_timestamp'] = 0

        if event.name not in thread['kvm_events']:
            thread['kvm_events'][event.name] = 0
        thread['kvm_events'][event.name] = thread['kvm_events'][event.name] + 1

        threads[current_tid] = thread

    # Printing
    filters = {'lttng': [2212, 2218, 2190, 13981, 2217, 13979], 'dd': [13980]}
    print("layer,tracer,maxprime,event,freq,total_event_cost,cost_per_event")
    for filter_name, ids in filters.items():
        for tid, thread in sorted(threads.items(), key=operator.itemgetter(0), reverse=False):
            # print('thread=%s'%tid)
            tids = tid.split('-')
            if int(tids[0]) not in ids and int(tids[1]) not in ids:
                continue

            kvm_exit_cost = thread['kvm_exit_cost']
            kvm_exit_freq = thread['kvm_exit_freq']
            for exit_reason, cost in sorted(kvm_exit_cost.items(), key=operator.itemgetter(1), reverse=True):
                freq = kvm_exit_freq[exit_reason]
                print("%s,%s,%s,%s,%s,%s,%s" % (
                    layer,
                    filter_name,
                    arg3,
                    EXIT_REASONS[exit_reason],
                    freq,
                    cost,
                    round(cost/freq, 2)
                ))

    # for tid, thread in sorted(threads.items(), key=operator.itemgetter(0), reverse=False):
    #     print('thread=%s'%tid)
    #     kvm_exit_cost = thread['kvm_exit_cost']
    #     kvm_exit_freq = thread['kvm_exit_freq']
    #     for exit_reason, cost in sorted(kvm_exit_cost.items(), key=operator.itemgetter(1), reverse=True):
    #         freq = kvm_exit_freq[exit_reason]
    #         print("\t%s,%s,%s,%s,%s,%s,%s" % (
    #             layer,
    #             tracer,
    #             arg3,
    #             EXIT_REASONS[exit_reason],
    #             freq,
    #             cost,
    #             round(cost / freq, 2)
    #         ))

if __name__ == "__main__":
    main(sys.argv[1:])