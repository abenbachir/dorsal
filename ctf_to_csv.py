#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from symbols import Symbols

function_entry_map = dict()
HELP = "Usage: python ctf_to_csv.py path/to/directory -o <outputfile>"
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

def add_level_call(call, depth):
    if depth not in level_calls:
        level_calls[depth] = []
    level_calls[depth].append(call)

def has_conflicts(call, depth):
    if depth not in level_calls:
        return False
    calls = level_calls[depth]
    for i in range(0, len(calls)):
        call1 = calls[i]
        call2 = call
        if not ((call1["start"] < call2["start"] and call1["end"] < call2["start"])
                        or (call2["start"] < call1["start"] and call2["end"] < call1["start"])):
            return True

def detect_conflicts(calls):
    count = 0
    for i in range(0, len(calls)):
        for j in range(0, len(calls)):
            if i == j:
                continue
            call1 = calls[i]
            call2 = calls[j]
            if not ( (call1["start"] < call2["start"] and call1["end"] < call2["start"])
                or (call2["start"] < call1["start"] and call2["end"] < call1["start"])):
                count += 1
    print("Conflicts found", count)


def add_metadata(events, name, pid, tid, args):
    events.append({
        'pid': pid,
        'tid': tid,
        'name': name,
        'ph': 'M',
        'cat': "__metadata",
        'args': args,
    })

def main(argv):
    output = None
    start_recording = 0
    path = ""
    try:
        path = argv[0]
    except:
        if not path:
            raise TypeError(HELP)

    try:
        opts, args = getopt.getopt(argv[1:], "hs:p:")
    except getopt.GetoptError:
        raise TypeError(HELP)

    for opt, arg in opts:
        if opt == '-h':
            raise TypeError(HELP)
        elif opt == '-o':
            output = arg

    if not output:
        output = "./trace.csv"

    # Create TraceCollection and add trace:
    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    with open(output, 'w+') as filewriter:
    filewriter.write("event,overhead\n")
    print("--- Converting traces ---")
    for event in traces.events:
 
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        filewriter.write("%s" % (event.name))
        #event.name
        #nr = fields['nr']
        
    print("--- Done ---")



if __name__ == "__main__":
    main(sys.argv[1:])

