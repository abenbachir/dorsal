#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from symbols import Symbols

function_entry_map = dict()
HELP = "Usage: python babeltrace_json.py path/to/directory -o <outputfile>"
CATEGORY = "LTTng"
overheads = dict()
USERSPACE_HYPERCALL_NR = 2000
KERNELSPACE_HYPERCALL_NR = 1000
SCHED_SWITCH_HYPERCALL_NR = 1001

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


def add_overhead(func_name, overhead):
    if func_name not in overheads:
        overheads[func_name] = []
    overheads[func_name].append(overhead)


def main(argv):
    output = None
    path = "/home/abder/lttng-traces/kernelspace-tracing-20161206-133458"
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
        output = "./traces/traces.json"

    # Create TraceCollection and add trace:
    program_symbols = Symbols("./program-symbols.txt")
    kernel_symbols = Symbols("./symbols.txt")
    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    print("--- Converting traces ---")
    # {"pid":0,"tid":0,"ts":1739397949814,"ph":"X","cat":"shutdown","name":"BrowserMainRunner","dur":186340,"tdur":6682,"tts":346077,"args":{}},
    trace_events = []
    count = 0
    for event in traces.events:
        # count += 1
        # if count > 10000:
        #     break
        if event.name != "kvm_x86_hypercall":
            continue
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        nr = fields['nr']
        is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
        if is_sched_switch:
            print("sched_switch",event.timestamp)
            trace_events.append({
                'pid': 0,
                'tid': 0,
                'name': 'sched_switch',
                'ph': 'i',
                'ts': ns_to_us(event.timestamp),
                's': 'g',
                'args': {
                    'wake_cpu': fields['a0']
                },
            })
        else:
            # function_name = get_kernel_symbol_name(function_address)
            function_address = fields['a0']
            is_entry = fields['a1'] == 0
            # Handle entry
            if is_entry:
                # add entry event until we find the exit event
                if function_address not in function_entry_map:
                    function_entry_map[function_address] = []

                function_entry_map[function_address].append({
                    'pid': 0,
                    'tid': 0,
                    'name': function_address,
                    'ph': 'X',
                    # 'cat': event.name,
                    'dur': 0,
                    'ts': event.timestamp,
                    'args': {'cpu_id_entry': fields['cpu_id']},
                })
            # Handle exit
            elif function_address in function_entry_map:
                if len(function_entry_map[function_address]) == 0:
                    print("not found ", function_address, kernel_symbols.get_kernel_symbol_name(function_address))
                    continue
                original_duration = fields['a2']
                event_json = function_entry_map[function_address].pop()
                event_json['name'] = kernel_symbols.get_symbol_name(function_address)
                duration = event.timestamp - event_json['ts']
                event_json['ts'] = ns_to_us(event_json['ts'])
                event_json['dur'] = ns_to_us(duration)
                event_json['tdur'] = ns_to_us(original_duration)
                event_json['tid'] = fields['cpu_id']
                event_json['args']['duration_ms'] = ns_to_ms(original_duration)
                event_json['args']['cpu_id_exit'] = fields['cpu_id']
                event_json['args']['depth'] = fields['a3']
                event_json['args']['overhead'] = round((1-(original_duration/duration)) * 100, 2)
                event_json['args']['wall_duration_ns'] = duration
                trace_events.append(event_json)
                add_overhead(event_json['name'], event_json['args']['overhead'])

    print("--- Done ---")
    # {"pid":15702,"tid":2,"ts":0,"ph":"M","cat":"__metadata","name":"process_labels","args":{"labels":"LTTng: an open source tracing framework for Linux"}},
    trace_events.append({
        'pid': 0,
        'tid': 0,
        'name': "process_labels",
        'ph': 'M',
        'cat': "__metadata",
        'args': {'labels': "Kernel space"},
    })

    content = json.dumps({"traceEvents": trace_events})
    with open(output, "w") as f:
        f.write(content)
    overhead_content = json.dumps({"func_overheads": overheads})
    overhead_output = os.path.join(os.path.dirname(output), "overhead_"+os.path.basename(output))
    with open(overhead_output, "w") as f:
        f.write(overhead_content)


if __name__ == "__main__":
    main(sys.argv[1:])

