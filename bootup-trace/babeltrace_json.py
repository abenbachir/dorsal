#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from kernel_symbol import get_symbol_name

HELP = "Usage: python babeltrace_json.py path/to/directory -o <outputfile>"
CATEGORY = "LTTng"

# TODO: return float
def ns_to_us(ns):
    return float(ns/float(100))


def format_value(field_type, value):
    if field_type == 1:
        return int(value)
    elif field_type == 2:
        return float(value)
    elif field_type == 8:
        return [x for x in value]
    else:
        return str(value)

function_entry_map = dict()

def main(argv):
    # try:
    #     path = argv[0]
    # except:
    #     raise TypeError(HELP)

    # try:
    #     opts, args = getopt.getopt(argv[1:], "hs:p:")
    # except getopt.GetoptError:
    #     raise TypeError(HELP)

    # output = None
    # for opt, arg in opts:
    #     if opt == '-h':
    #         raise TypeError(HELP)
    #     elif opt == '-o':
    #         output = arg

    # if not output:
    #     output = "trace.json"

    path = "/home/abder/lttng-traces/bootup-tracing-20161201-174012/kernel"

    # Create TraceCollection and add trace:
    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_trace(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    # Listing events
    # print("--- Event list ---")
    # for event_declaration in trace_handle.events:
    #     print("event : {}".format(event_declaration.name))
    #     if event_declaration.name == "sched_switch":
    #         for field_declaration in event_declaration.fields:
    #             print(field_declaration)
    # print("--- Done ---")

    print("--- Converting traces ---")
    # {"pid":0,"tid":0,"ts":1739397949814,"ph":"X","cat":"shutdown","name":"BrowserMainRunner","dur":186340,"tdur":6682,"tts":346077,"args":{}},
    trace_events = []
    count = 0
    for event in traces.events:
        if count > 1000:
            break
        if event.name != "kvm_x86_hypercall":
            continue
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)
        function_address = fields['a0']
        if function_address in function_entry_map:
            event_json = function_entry_map[function_address]
            event_json['name'] = get_symbol_name(function_address)
            duration = ns_to_us(event.timestamp) - event_json['ts']
            event_json['dur'] = duration
            trace_events.append(event_json)
            del function_entry_map[function_address]
        else:
            # add entry event until we find the exit event
            function_entry_map[function_address] = {
                'pid': 0,
                'tid': 0,
                'name': function_address,
                'ph': 'X',
                'cat': event.name,
                'dur': 0,
                'tdur': 0,
                'ts': ns_to_us(event.timestamp),
                'tts': 0,
            }
        count += 1
    print("--- Done ---")
    content = json.dumps({"traceEvents": trace_events})
    with open("./traces.json", "w") as f:
        f.write(content)


if __name__ == "__main__":
    main(sys.argv[1:])

