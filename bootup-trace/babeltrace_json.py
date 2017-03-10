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
    path = "~/lttng-traces/kernelspace-tracing-20161207-135859"
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

    trace_events = []
    statistics = "function_name,guest_duration,host_duration,overhead,depth\n"
    print("--- Converting traces ---")
    for event in traces.events:
        if event.name != "kvm_x86_hypercall":
            continue

        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        nr = fields['nr']
        is_sched_switch = (nr == SCHED_SWITCH_HYPERCALL_NR)
        if is_sched_switch:
            # trace_events.append({
            #     'pid': 0,
            #     'tid': 0,
            #     'name': 'sched_switch',
            #     'ph': 'i',
            #     'ts': ns_to_us(event.timestamp),
            #     's': 'g',
            #     'args': {
            #         'cpu': fields['a1'],
            #         'success': fields['a0']
            #     },
            # })
            nr
        else:
            is_kernelspace = (nr == KERNELSPACE_HYPERCALL_NR)
            is_userspace = (nr == USERSPACE_HYPERCALL_NR)
            function_address = fields['a0']
            function_name = function_address
            if is_kernelspace:
                function_name = kernel_symbols.get_name(function_address)
            if is_userspace:
                function_name = program_symbols.get_name(function_address)
            if function_name == "main":
                start_recording = True

            if not start_recording:
                continue

            is_entry = fields['a1'] == 0
            if is_entry:
                # add entry event until we find the exit event
                if function_address not in function_entry_map:
                    function_entry_map[function_address] = []

                depth = fields["a3"]
                if is_kernelspace:
                    call = {'start': event.timestamp, 'end': event.timestamp + 10, 'name': function_name}
                    if has_conflicts(call, depth):
                        continue

                function_entry_map[function_address].append({
                    'pid': 0,
                    'tid': nr,
                    'name': function_address,
                    'ph': 'X',
                    'dur': 0,
                    'ts': event.timestamp,
                    'args': {
                        # 'cpu_id_entry': fields['cpu_id'],
                        'cpu': fields['a2'],
                        'depth': depth
                    },
                })
            # Handle exit
            elif function_address in function_entry_map:
                if len(function_entry_map[function_address]) == 0:
                    print("not found", function_address, function_name)
                    continue
                event_json = function_entry_map[function_address].pop()
                guest_duration = fields['a2']
                depth = fields['a3']
                host_duration = event.timestamp - event_json['ts']
                overhead = round((1 - (guest_duration / host_duration)) * 100, 2)
                # if is_kernelspace:
                #     call = {'start': event_json['ts'], 'end': event.timestamp, 'name': function_name}
                #     if has_conflicts(call, depth):
                #         continue
                #     add_level_call(call, depth)

                event_json['name'] = function_name
                event_json['ts'] = ns_to_us(event_json['ts'])
                event_json['dur'] = ns_to_us(host_duration)
                event_json['tdur'] = ns_to_us(guest_duration)
                event_json['args']['depth'] = depth
                event_json['args']['overhead'] = overhead
                event_json['args']['guest_duration_ns'] = guest_duration
                # event_json['args']['cpu_id_exit'] = fields['cpu_id']
                event_json['args']['host_duration_ns'] = host_duration
                trace_events.append(event_json)
                statistics += '"{}",{},{},{}\n'.format(function_name, guest_duration, host_duration, overhead, depth)

                if function_name == "main":
                    start_recording = False
    print("--- Done ---")
    add_metadata(trace_events, "thread_name", 0, KERNELSPACE_HYPERCALL_NR, {'name': "Kernelspace"})
    add_metadata(trace_events, "thread_name", 0, USERSPACE_HYPERCALL_NR, {'name': "Userspace"})
    add_metadata(trace_events, "process_name", 0, USERSPACE_HYPERCALL_NR, {'name': "VM0"})
    add_metadata(trace_events, "process_labels", 0, USERSPACE_HYPERCALL_NR, {'labels': "Ubuntu 16.04"})
    add_metadata(trace_events, "thread_sort_index", 0, KERNELSPACE_HYPERCALL_NR, {'sort_index': -5})
    add_metadata(trace_events, "thread_sort_index", 0, USERSPACE_HYPERCALL_NR, {'sort_index': -10})

    content = json.dumps({
        "traceEvents": trace_events,
        "displayTimeUnit": "ns"
    })
    with open(output, "w") as f:
        f.write(content)
    # detect_conflicts(level_calls)
    statistics_output = "./rscript/statistics_"+os.path.splitext(os.path.basename(output))[0]+".csv"
    with open(statistics_output, "w") as file:
        file.write(statistics)


if __name__ == "__main__":
    main(sys.argv[1:])

