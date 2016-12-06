#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from kernel_symbol import get_symbol_name

function_entry_map = dict()
HELP = "Usage: python babeltrace_json.py path/to/directory -o <outputfile>"
CATEGORY = "LTTng"
overheads = dict()


def ns_to_us(ns):
    return ns/float(10^3)

def ns_to_ms(ns):
    return ns/float(10^6)

def format_value(field_type, value):
    if field_type == 1:
        return int(value)
    elif field_type == 2:
        return float(value)
    elif field_type == 8:
        return [x for x in value]
    else:
        return str(value)

def add_overhead(func_name, overhead):
    if func_name not in overheads:
        overheads[func_name] = []
    overheads[func_name].append(overhead)

def main(argv):
    output = None
    # try:
    #     path = argv[0]
    # except:
    #     raise TypeError(HELP)
    #
    # try:
    #     opts, args = getopt.getopt(argv[1:], "hs:p:")
    # except getopt.GetoptError:
    #     raise TypeError(HELP)
    #
    #
    # for opt, arg in opts:
    #     if opt == '-h':
    #         raise TypeError(HELP)
    #     elif opt == '-o':
    #         output = arg

    if not output:
        output = "traces.json"
    # if not path:
    path = "/home/abder/lttng-traces/bootup-tracing-20161205-171305"


    # Create TraceCollection and add trace:
    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
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
        if event.name != "kvm_x86_hypercall":
            continue
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        function_address = fields['a0']
        is_entry = fields['a1'] == 0
        if is_entry:
            # add entry event until we find the exit event
            if function_address not in function_entry_map:
                function_entry_map[function_address] = []
            function_entry_map[function_address].append({
                'pid': 0,
                'tid': 0,
                'cpu_id': fields['cpu_id'],
                'name': function_address,
                'ph': 'X',
                'cat': event.name,
                'dur': 0,
                # 'tdur': 0,
                # 'tts': 0,
                'ts': event.timestamp,
                'args': {'duration': fields['a1'], 'cpu_id_entry': fields['cpu_id']},
            })
        elif function_address in function_entry_map:
            if len(function_entry_map[function_address]) == 0:
                print("not found ", function_address, get_symbol_name(function_address))
                continue
            event_json = function_entry_map[function_address].pop()
            event_json['name'] = get_symbol_name(function_address)
            duration = ns_to_us(event.timestamp - event_json['ts'])
            event_json['ts'] = ns_to_us(event_json['ts'])
            event_json['dur'] = duration
            event_json['args']['duration'] = ns_to_ms(fields['a2'])
            event_json['args']['cpu_id_exit'] = fields['cpu_id']
            trace_events.append(event_json)
            add_overhead(event_json['name'], ns_to_ms((event.timestamp - event_json['ts']) - int(fields['a2'])) )
            # del function_entry_map[function_address]

        count += 1
    print("--- Done ---")
    print(overheads)
    content = json.dumps({"traceEvents": trace_events})
    with open(output, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main(sys.argv[1:])

