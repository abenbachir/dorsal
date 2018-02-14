#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.writer as btw
import babeltrace.reader

try:
    from .utils import *
except Exception as ex:
    from utils import *


per_cpu_streams = {}


def main(argv):
    path = "/home/abder/lttng-traces/bootevel-20180208-184457"
    output = None
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

    path = path.rstrip('/')
    kernel_symbols_path = os.path.join(path, "mapping/kallsyms.map")
    kernel_symbols_l1_path = os.path.join(path, "mapping/kallsyms-l1.map")
    process_symbols_l1_path = os.path.join(path, "mapping/process-l1.map")

    # Create TraceCollection and add trace:
    kernel_symbols = Symbols(kernel_symbols_path)
    kernel_symbols_l1 = Symbols(kernel_symbols_l1_path)
    process_symbols_l1 = Process(process_symbols_l1_path)
    hash_table = HashTable(kernel_symbols_path)

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    # temporary directory holding the CTF trace
    trace_path = "%s-converted" % (path)
    print(trace_path)
    # os.system('mkdir -p ' + trace_path+'/mapping')
    # os.system('cp ' + os.path.join(path, "mapping/kallsyms*") + ' ' + trace_path+'/mapping')

    kernel_event_classes = {}
    ust_event_classes = {}
    kernel_event_classes['guest'] = babeltrace_create_writer("guest-kernel", trace_path, per_cpu_streams)
    # ust_event_classes['guest'] = create_writer("guest-ust", trace_path)

    for event in traces.events:
        events = []
        cpu_id = event['cpu_id']
        is_guest_event = is_hypercall_event(event.name)
        layer = "guest" if is_guest_event else "host"

        if not is_guest_event:
            continue

        vcpu_id, events = handle_l1_event(event)
        # cpu_id = vcpu_id

        for myevent in events:
            is_ust = isinstance(myevent, EventFunction)
            mode = "ust" if is_ust else "kernel"
            stream_name = layer + '-' + mode
            timestamp = myevent['timestamp'] if 'timestamp' in myevent else event.timestamp

            # UST Events
            if is_ust:
                if process_symbols_l1.get_name(myevent.tid) is not None:
                    myevent.procname = "Guest: " + process_symbols_l1.get_name(myevent.tid)
                name = hash_table.get_name(myevent.hash_code)
                if name is None:
                    name = kernel_symbols_l1.get_name(myevent.address)
                myevent.function_name = kernel_symbols_l1.get_name(myevent.address)
                # quick hack to use only one kallsyms file : Convert guest addr to host addr
                # if kernel_symbols.get_addr(myevent.function_name) :
                #     myevent.address = kernel_symbols.get_addr(myevent.function_name)

                if isinstance(myevent, FunctionEntry):
                    func_entry_class = ust_event_classes[layer][FUNC_ENTRY_EVENT_NAME]
                    entry_event = btw.Event(func_entry_class)
                    entry_event.clock().time = myevent.timestamp
                    entry_event.payload(ADDR_FIELD_NAME).value = myevent.address
                    entry_event.payload(VTID_FIELD_NAME).value = myevent.tid
                    entry_event.payload(VPID_FIELD_NAME).value = myevent.pid
                    entry_event.payload(PROCNAME_FIELD_NAME).value = myevent.procname
                    per_cpu_streams[stream_name][myevent.cpu_id].append_event(entry_event)
                elif isinstance(myevent, FunctionExit):
                    func_exit_class = ust_event_classes[layer][FUNC_EXIT_EVENT_NAME]
                    exit_event = btw.Event(func_exit_class)
                    exit_event.clock().time = event.timestamp
                    exit_event.payload(ADDR_FIELD_NAME).value = myevent.address
                    exit_event.payload(VTID_FIELD_NAME).value = myevent.tid
                    exit_event.payload(VPID_FIELD_NAME).value = myevent.pid
                    exit_event.payload(PROCNAME_FIELD_NAME).value = myevent.procname
                    per_cpu_streams[stream_name][myevent.cpu_id].append_event(exit_event)
            # Kernel Events
            elif isinstance(myevent, dict):
                try:
                    event_classes = kernel_event_classes[layer]
                    event_class = event_classes[myevent['type']]
                    payload = myevent["payload"]
                    new_event = btw.Event(event_class)

                    # override clock if timestamp been found in myevent
                    if 'timestamp' in myevent:
                        new_event.clock().time = myevent['timestamp']
                    else:
                        new_event.clock().time = event.timestamp

                    for name, value in payload.items():
                        try:
                            if "comm" in name:
                                event_field = new_event.payload(name)
                                for j in range(COMM_LENGTH):
                                    if j < len(value):
                                        event_field.field(j).value = ord(value[j])
                                    else:
                                        event_field.field(j).value = 0
                            else:
                                new_event.payload(name).value = value
                        except Exception as ex:
                            print(ex)

                        per_cpu_streams[stream_name][cpu_id].append_event(new_event)
                except Exception as ex:
                    event.timestamp
                    # print(event.timestamp, myevent, ex)


    # flush the streams
    for domain, streams in per_cpu_streams.items():
        print("%s flushing streams ..." % domain)
        for i in range(0, len(streams)):
            streams[i].flush()


if __name__ == "__main__":
    main(sys.argv[1:])

