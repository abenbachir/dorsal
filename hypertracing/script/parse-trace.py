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
        if not os.path.exists(path):
            raise Exception("path not found : %s"%path)
        if len(argv) > 1:
            print_header = int(argv[1])
    except Exception as ex:
        raise TypeError()

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    splits = os.path.basename(path).split('-')
    layer = splits[0].upper()
    workload = splits[1]
    tracer = splits[2].capitalize()
    configuration = splits[3]
    start_time = 0
    elapsed_time = 0
    elapsed_time_from_hypercall = 0
    for event in traces.events:
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)
        timestamp = event.timestamp

        # Handle hypercall
        if event.name == "kvm_x86_hypercall":
            hp = fields['nr'] + fields['a0'] + fields['a1'] + fields['a2']
            if hp == 0:
                start_time = timestamp
                continue
            if hp == 4:
                elapsed_time_from_hypercall = timestamp - start_time
                elapsed_time = fields['a3']
                continue

    if print_header > 0:
        print("layer,tracer,workload,configuration,time")

    print("%s,%s,%s,%s,%s" % (
        layer, tracer, workload, configuration, elapsed_time
    ))

if __name__ == "__main__":
    main(sys.argv[1:])