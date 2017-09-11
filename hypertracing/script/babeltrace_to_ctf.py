#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
import babeltrace.writer as btw
from utils import *
import multiprocessing

VTID_FIELD_NAME = "vtid"
VPID_FIELD_NAME = "vpid"
ADDR_FIELD_NAME = "addr"
NAME_FIELD_NAME = "name"
PROCNAME_FIELD_NAME = "procname"
FUNC_ENTRY_EVENT_NAME = "func_entry"
FUNC_EXIT_EVENT_NAME = "func_exit"
SCHED_SWITCH_EVENT_NAME = "sched_switch"
PREV_COMM_FIELD_NAME = "_prev_comm"

def main(argv):
    path = "/home/abder/lttng-traces/hypergraph-20170910-204405"
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

    # temporary directory holding the CTF trace
    trace_path = "/home/abder/lttng-traces/fgraph-traces"
    # our writer
    kernel_writer = btw.Writer(os.path.join(trace_path, "kernel"))
    ust_writer = btw.Writer(os.path.join(trace_path, "ust"))
    # create one default clock and register it to the writer
    clock1 = btw.Clock('monotonic')
    clock2 = btw.Clock('monotonic')
    kernel_writer.add_clock(clock1)
    kernel_writer.add_environment_field("domain", "kernel")
    kernel_writer.add_environment_field("tracer_name", "lttng")
    ust_writer.add_clock(clock2)
    ust_writer.add_environment_field("domain", "ust")
    ust_writer.add_environment_field("tracer_name", "lttng")
    # create one default stream class and assign our clock to it
    kernel_stream_class = btw.StreamClass('channel')
    kernel_stream_class.clock = clock1
    ust_stream_class = btw.StreamClass('channel')
    ust_stream_class.clock = clock2

    # create fields
    int8_type = btw.IntegerFieldDeclaration(8)
    int8_type.signed = 1
    int8_type.encoding = babeltrace.common.CTFStringEncoding.UTF8
    int8_type.alignment = 8

    array_type = btw.ArrayFieldDeclaration(int8_type, 20)
    int32_type = btw.IntegerFieldDeclaration(32)
    int32_type.signed = 1
    uint32_type = btw.IntegerFieldDeclaration(32)
    uint32_type.signed = 0
    uint32_type.alignment = 8
    uint64_type = btw.IntegerFieldDeclaration(64)
    uint64_type.signed = 0
    uint64_type.alignment = 8
    int64_type = btw.IntegerFieldDeclaration(64)
    int64_type.signed = 1
    string_type = btw.StringFieldDeclaration()
    string_type.encoding = babeltrace.common.CTFStringEncoding.UTF8

    packet_context_type = ust_stream_class.packet_context_type
    packet_context_type.add_field(uint32_type, "cpu_id")
    ust_stream_class.packet_context_type = packet_context_type

    packet_context_type = kernel_stream_class.packet_context_type
    packet_context_type.add_field(uint32_type, "cpu_id")
    kernel_stream_class.packet_context_type = packet_context_type

    # Set a stream event context
    # stream_event_context_type = btw.StructureFieldDeclaration()
    # stream_event_context_type.add_field(uint32_type, "cpu_id")
    # stream_class.event_context_type = stream_event_context_type

    # add this field declaration to event class
    func_entry_event_class = btw.EventClass(FUNC_ENTRY_EVENT_NAME)
    func_entry_event_class.add_field(uint64_type, ADDR_FIELD_NAME)
    func_entry_event_class.add_field(uint32_type, VTID_FIELD_NAME)
    func_entry_event_class.add_field(uint32_type, VPID_FIELD_NAME)
    func_entry_event_class.add_field(string_type, PROCNAME_FIELD_NAME)
    ust_stream_class.add_event_class(func_entry_event_class)

    func_exit_event_class = btw.EventClass(FUNC_EXIT_EVENT_NAME)
    func_exit_event_class.add_field(uint64_type, ADDR_FIELD_NAME)
    func_exit_event_class.add_field(int32_type, VTID_FIELD_NAME)
    func_exit_event_class.add_field(int32_type, VPID_FIELD_NAME)
    func_exit_event_class.add_field(string_type, PROCNAME_FIELD_NAME)
    ust_stream_class.add_event_class(func_exit_event_class)

    sched_switch_event_class = btw.EventClass(SCHED_SWITCH_EVENT_NAME)
    sched_switch_event_class.add_field(array_type, "prev_comm")
    sched_switch_event_class.add_field(int32_type, "prev_tid")
    sched_switch_event_class.add_field(int32_type, "prev_prio")
    sched_switch_event_class.add_field(int64_type, "prev_state")
    sched_switch_event_class.add_field(array_type, "next_comm")
    sched_switch_event_class.add_field(int32_type, "next_tid")
    sched_switch_event_class.add_field(int32_type, "next_prio")
    kernel_stream_class.add_event_class(sched_switch_event_class)

    sys_entry_open_event_class = btw.EventClass("syscall_entry_open")
    # sys_entry_open_event_class.add_field(int32_type, "fd")
    kernel_stream_class.add_event_class(sys_entry_open_event_class)
    sys_exit_open_event_class = btw.EventClass("syscall_exit_open")
    sys_exit_open_event_class.add_field(int32_type, "ret")
    kernel_stream_class.add_event_class(sys_exit_open_event_class)

    # create our single stream
    cpu_count = multiprocessing.cpu_count()
    per_cpu_streams = {'ust': [], 'kernel': []}
    # ust streams
    for i in range(0, cpu_count):
        ust_stream = ust_writer.create_stream(ust_stream_class)
        ust_stream.packet_context.field("cpu_id").value = i
        per_cpu_streams['ust'].append(ust_stream)
    # kernel streams
    for i in range(0, cpu_count):
        kernel_stream = kernel_writer.create_stream(kernel_stream_class)
        kernel_stream.packet_context.field("cpu_id").value = i
        per_cpu_streams['kernel'].append(kernel_stream)

    kallsyms = {}
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
                # quick hack to use only one kallsyms file : Convert guest addr to host addr
                if kernel_symbols.get_addr(event_obj.function_name) :
                    event_obj.address = kernel_symbols.get_addr(event_obj.function_name)
        else:
            event_obj = handle_l0_event(event)
            if isinstance(event_obj, EventFunction):
                # print(event_obj.virt_level, kernel_symbols.get_name(event_obj.address), hash_table.get_name(event_obj.hash_code))
                event_obj.function_name = kernel_symbols.get_name(event_obj.address)

        if event_obj is None:
            continue

        # if isinstance(event_obj, FunctionEntryExit) and event_obj.cpu_id != 0:
        #     continue

        if isinstance(event_obj, FunctionEntry):
            entry_event = btw.Event(func_entry_event_class)
            entry_event.clock().time = event_obj.timestamp
            entry_event.payload(ADDR_FIELD_NAME).value = event_obj.address
            entry_event.payload(VTID_FIELD_NAME).value = event_obj.tid
            entry_event.payload(VPID_FIELD_NAME).value = event_obj.pid
            entry_event.payload(PROCNAME_FIELD_NAME).value = event_obj.procname
            per_cpu_streams['ust'][event_obj.cpu_id].append_event(entry_event)

            if event_obj.function_name.lower() == "sys_open":
                syscall_event_entry = btw.Event(sys_entry_open_event_class)
                syscall_event_entry.clock().time = event_obj.timestamp
                per_cpu_streams['kernel'][event_obj.cpu_id].append_event(syscall_event_entry)

        if isinstance(event_obj, FunctionExit):
            exit_event = btw.Event(func_exit_event_class)
            exit_event.clock().time = event_obj.timestamp
            exit_event.payload(ADDR_FIELD_NAME).value = event_obj.address
            exit_event.payload(VTID_FIELD_NAME).value = event_obj.tid
            exit_event.payload(VPID_FIELD_NAME).value = event_obj.pid
            exit_event.payload(PROCNAME_FIELD_NAME).value = event_obj.procname
            per_cpu_streams['ust'][event_obj.cpu_id].append_event(exit_event)
            if event_obj.function_name.lower() == "sys_open":
                syscall_event_exit = btw.Event(sys_exit_open_event_class)
                syscall_event_exit.clock().time = event_obj.timestamp
                syscall_event_exit.payload("ret").value = 1
                per_cpu_streams['kernel'][event_obj.cpu_id].append_event(syscall_event_exit)

        if isinstance(event_obj, dict):
            # print(event_obj)
            if event_obj['type'] == SCHED_SWITCH_EVENT_NAME:
                fields = event_obj["fields"]
                sched_event = btw.Event(sched_switch_event_class)
                sched_event.clock().time = event.timestamp
                prev_comm_field = sched_event.payload("prev_comm")
                next_comm_field = sched_event.payload("next_comm")

                for j in range(20):
                    if j < len(fields["prev_comm"]):
                        prev_comm_field.field(j).value = ord(fields["prev_comm"][j])
                    else:
                        prev_comm_field.field(j).value = 0
                    if j < len(fields["next_comm"]):
                        next_comm_field.field(j).value = ord(fields["next_comm"][j])
                    else:
                        next_comm_field.field(j).value = 0

                sched_event.payload("prev_tid").value = fields["prev_tid"]
                sched_event.payload("prev_prio").value = fields["prev_prio"]
                sched_event.payload("prev_state").value = fields["prev_state"]
                sched_event.payload("next_tid").value = fields["next_tid"]
                sched_event.payload("next_prio").value = fields["next_prio"]
                per_cpu_streams['kernel'][fields['cpu_id']].append_event(sched_event)

    # flush the streams

    for domain, streams in per_cpu_streams.items():
        print("%s flushing streams" % domain)
        for i in range(0, len(streams)):
            streams[i].flush()

if __name__ == "__main__":
    main(sys.argv[1:])

