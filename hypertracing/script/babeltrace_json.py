#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from utils import *

function_entry_map = dict()
PH_ENTRY = "B"
PH_EXIT = "E"

cpu_metadatas = dict()
def to_chrome_entry_exit_event(event_obj, ph):
    # ts = "%s.%s" % (event_obj.timestamp//1000, event_obj.timestamp % 1000)
    ts = ns_to_us(event_obj.timestamp)
    # ts = event_obj.timestamp
    event = {
        'pid': "%s - CPU %s - %s(pid %s)" % (event_obj.virt_level, event_obj.cpu_id, event_obj.procname, event_obj.pid),
        'tid': event_obj.tid,
        'name': event_obj.function_name,
        'ph': ph,
        'ts': ts,
        'cat': event_obj.virt_level,
        'args': {
            'cpu': event_obj.cpu_id,
            'depth': event_obj.depth,
            'duration': event_obj.dur
        },
    }

    cpu_metadatas[event_obj.cpu_id] = 1
    return event


def to_chrome_dur_event(event_obj):
    event = {
        'pid': "%s - %s (pid %s)" % (event_obj.virt_level, event_obj.procname, event_obj.pid),
        'tid': event_obj.tid,
        'name': event_obj.function_name,
        'ph': 'X',
        'dur': ns_to_us(event_obj.dur),
        'tdur': ns_to_us(event_obj.dur),
        'ts': ns_to_us(event_obj.timestamp),
        'tts': ns_to_us(event_obj.timestamp),
        'cat': event_obj.virt_level,
        'args': {
            # 'cpu_id_entry': fields['cpu_id'],
            'cpu': event_obj.cpu_id,
            'depth': event_obj.depth,
            'duration': event_obj.dur
        },
    }
    cpu_metadatas[event_obj.cpu_id] = 1
    return event

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
    path = "/home/abder/lttng-traces/hypergraph-20170908-200840"
    output = None
    input_cpuid = None
    kernel_symbols_path = "/home/abder/utils/hypertracing/script/kallsyms.map"
    kernel_symbols_l1_path = "/home/abder/utils/hypertracing/script/kallsyms-l1.map"
    try:
        if len(argv) > 0:
            path = argv[0]
            # kernel_symbols_path = argv[1]
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
        elif opt == '-o':
            output = arg

    if not output:
        output = "traces.json"

    # Create TraceCollection and add trace:
    kernel_symbols = Symbols(kernel_symbols_path)
    kernel_symbols_l1 = Symbols(kernel_symbols_l1_path)
    hash_table = HashTable(kernel_symbols_path)
    process_list = Process("./script/process.txt")

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    print("--- Converting traces ---")
    trace_events = []
    count = 0
    start = 0
    for event in traces.events:
        event_obj = None
        if is_hypercall_event(event.name):
            start = 1
            event_obj = handle_l1_event(event)
            if isinstance(event_obj, EventFunction):
                name = hash_table.get_name(event_obj.hash_code)
                if name is None:
                    name = kernel_symbols_l1.get_name(event_obj.address)
                event_obj.function_name = kernel_symbols_l1.get_name(event_obj.address)
        else:
            event_obj = handle_l0_event(event)
            if isinstance(event_obj, EventFunction):
                # print(event_obj.virt_level, kernel_symbols.get_name(event_obj.address), hash_table.get_name(event_obj.hash_code))
                event_obj.function_name = kernel_symbols.get_name(event_obj.address)

        if event_obj is None:
            continue

        # if isinstance(event_obj, EventFunction) and event_obj.cpu_id != 0:
        #     continue
        if isinstance(event_obj, FunctionExitOnly):
            # timestamp_entry = event_obj.timestamp - event_obj.dur
            # event_json = to_chrome_entry_exit_event(event_obj, PH_EXIT)
            # trace_events.append(event_json)
            #
            # event_obj.timestamp = timestamp_entry
            # event_json = to_chrome_entry_exit_event(event_obj, PH_ENTRY)
            # trace_events.append(event_json)

            event_obj.timestamp = event_obj.timestamp - event_obj.dur
            event_json = to_chrome_dur_event(event_obj)
            trace_events.append(event_json)

        if isinstance(event_obj, FunctionEntry):
            event_json = to_chrome_entry_exit_event(event_obj, PH_ENTRY)
            trace_events.append(event_json)

        if isinstance(event_obj, FunctionExit):
            count += 1
            event_json = to_chrome_entry_exit_event(event_obj, PH_EXIT)
            trace_events.append(event_json)
        # if count > 50000:
        #     break

    # add_metadata(trace_events, "thread_name", 0, KERNELSPACE_HYPERCALL_NR, {'name': "Kernelspace"})
    # add_metadata(trace_events, "thread_name", 0, USERSPACE_HYPERCALL_NR, {'name': "Userspace"})
    # add_metadata(trace_events, "process_name", 0, USERSPACE_HYPERCALL_NR, {'name': "VM0"})
    # add_metadata(trace_events, "process_labels", 0, USERSPACE_HYPERCALL_NR, {'labels': "Ubuntu 16.04"})
    # add_metadata(trace_events, "thread_sort_index", 0, KERNELSPACE_HYPERCALL_NR, {'sort_index': -5})
    # add_metadata(trace_events, "thread_sort_index", 0, USERSPACE_HYPERCALL_NR, {'sort_index': -10})

    # for cpu_id, val in cpu_metadatas.items():
    #     add_metadata(trace_events, "process_name", cpu_id, 0, {'name': "-"})
    #     add_metadata(trace_events, "thread_sort_index", cpu_id, 0, {'sort_index': -5})
        # add_metadata(trace_events, "process_labels", cpu_id, 0, {'labels': "CPU "})


    content = json.dumps({
        "traceEvents": trace_events,
        "displayTimeUnit": "ns"
    })
    with open(output, "w") as f:
        f.write(content)
    print("--- Done ---")


if __name__ == "__main__":
    main(sys.argv[1:])

