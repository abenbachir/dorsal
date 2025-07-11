#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
import babeltrace.writer as btw
import multiprocessing
try:
    from .utils import *
except Exception as ex:
    from utils import *



KERNEL_MODE = "kernel"
USER_MODE = "ust"

# create global fields
int8_type = btw.IntegerFieldDeclaration(8)
int8_type.signed = 1
int8_type.encoding = babeltrace.common.CTFStringEncoding.UTF8
int8_type.alignment = 8
array_type = btw.ArrayFieldDeclaration(int8_type, COMM_LENGTH)

string_type = btw.StringFieldDeclaration()
string_type.encoding = babeltrace.common.CTFStringEncoding.UTF8

int32_type = btw.IntegerFieldDeclaration(32)
int32_type.signed = 1
int64_type = btw.IntegerFieldDeclaration(64)
int64_type.signed = 1
uint32_type = btw.IntegerFieldDeclaration(32)
uint32_type.signed = 0
uint32_type.alignment = 8
uint64_type = btw.IntegerFieldDeclaration(64)
uint64_type.signed = 0
uint64_type.alignment = 8


syscall_list_filepath = "/home/abder/utils/hypertracing/script/syscall_64.tbl"
cpu_count = multiprocessing.cpu_count()
per_cpu_streams = {}


def create_writer(stream_name, path):
    writer = btw.Writer(os.path.join(path, stream_name))
    clock = btw.Clock('monotonic')
    writer.add_clock(clock)
    writer.add_environment_field("domain", stream_name.split('-')[1])
    if KERNEL_MODE in stream_name:
        writer.add_environment_field("tracer_name", "lttng-modules")
        writer.add_environment_field("tracer_major", 2)
        writer.add_environment_field("tracer_minor", 10)
    else:
        writer.add_environment_field("tracer_name", "lttng-ust")

    stream_class = btw.StreamClass('channel')
    stream_class.clock = clock

    packet_context_type = stream_class.packet_context_type
    packet_context_type.add_field(uint32_type, "cpu_id")
    stream_class.packet_context_type = packet_context_type

    event_classes = {}
    if KERNEL_MODE in stream_name:
        # Sched switch
        sched_switch_event_class = btw.EventClass(SCHED_SWITCH_EVENT_NAME)
        sched_switch_event_class.add_field(array_type, "prev_comm")
        sched_switch_event_class.add_field(int32_type, "prev_tid")
        sched_switch_event_class.add_field(int32_type, "prev_prio")
        sched_switch_event_class.add_field(int64_type, "prev_state")
        sched_switch_event_class.add_field(array_type, "next_comm")
        sched_switch_event_class.add_field(int32_type, "next_tid")
        sched_switch_event_class.add_field(int32_type, "next_prio")
        stream_class.add_event_class(sched_switch_event_class)
        event_classes[SCHED_SWITCH_EVENT_NAME] = sched_switch_event_class
        # sched process fork
        sched_process_fork_event_class = btw.EventClass(SCHED_PROCESS_FORK_EVENT_NAME)
        sched_process_fork_event_class.add_field(array_type, "parent_comm")
        sched_process_fork_event_class.add_field(int32_type, "parent_tid")
        sched_process_fork_event_class.add_field(int32_type, "parent_pid")
        sched_process_fork_event_class.add_field(array_type, "child_comm")
        sched_process_fork_event_class.add_field(int32_type, "child_tid")
        sched_process_fork_event_class.add_field(int32_type, "child_pid")
        stream_class.add_event_class(sched_process_fork_event_class)
        event_classes[SCHED_PROCESS_FORK_EVENT_NAME] = sched_process_fork_event_class
        # sched process exit
        sched_process_exit_event_class = btw.EventClass(SCHED_PROCESS_EXIT_EVENT_NAME)
        sched_process_exit_event_class.add_field(int32_type, "tid")
        sched_process_exit_event_class.add_field(int32_type, "prio")
        sched_process_exit_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_process_exit_event_class)
        event_classes[SCHED_PROCESS_EXIT_EVENT_NAME] = sched_process_exit_event_class
        # sched process free
        sched_process_free_event_class = btw.EventClass(SCHED_PROCESS_FREE_EVENT_NAME)
        sched_process_free_event_class.add_field(int32_type, "tid")
        sched_process_free_event_class.add_field(int32_type, "prio")
        sched_process_free_event_class.add_field(array_type, "comm")
        stream_class.add_event_class(sched_process_free_event_class)
        event_classes[SCHED_PROCESS_FREE_EVENT_NAME] = sched_process_free_event_class
        # softirq raise
        softirq_raise_event_class = btw.EventClass(SOFTIRQ_RAISE_EVENT_NAME)
        softirq_raise_event_class.add_field(uint32_type, "vec")
        stream_class.add_event_class(softirq_raise_event_class)
        event_classes[SOFTIRQ_RAISE_EVENT_NAME] = softirq_raise_event_class
        # softirq entry
        softirq_entry_event_class = btw.EventClass(SOFTIRQ_ENTRY_EVENT_NAME)
        softirq_entry_event_class.add_field(uint32_type, "vec")
        stream_class.add_event_class(softirq_entry_event_class)
        event_classes[SOFTIRQ_ENTRY_EVENT_NAME] = softirq_entry_event_class
        # softirq exit
        softirq_exit_event_class = btw.EventClass(SOFTIRQ_EXIT_EVENT_NAME)
        softirq_exit_event_class.add_field(uint32_type, "vec")
        stream_class.add_event_class(softirq_exit_event_class)
        event_classes[SOFTIRQ_EXIT_EVENT_NAME] = softirq_exit_event_class
        # irq handler entry
        irq_handler_entry_event_class = btw.EventClass(IRQ_HANDLER_ENTRY_EVENT_NAME)
        irq_handler_entry_event_class.add_field(int32_type, "irq")
        irq_handler_entry_event_class.add_field(string_type, "name")
        stream_class.add_event_class(irq_handler_entry_event_class)
        event_classes[IRQ_HANDLER_ENTRY_EVENT_NAME] = irq_handler_entry_event_class
        # irq handler exit
        irq_handler_exit_event_class = btw.EventClass(IRQ_HANDLER_EXIT_EVENT_NAME)
        irq_handler_exit_event_class.add_field(int32_type, "irq")
        irq_handler_exit_event_class.add_field(int32_type, "ret")
        stream_class.add_event_class(irq_handler_exit_event_class)
        event_classes[IRQ_HANDLER_EXIT_EVENT_NAME] = irq_handler_exit_event_class

        # syscall event class
        syscalls = set([x['name'] for x in load_syscalls(syscall_list_filepath).values()])
        for name in syscalls:
            sys_entry_event_class = btw.EventClass("syscall_entry_%s" % name)
            sys_exit_event_class = btw.EventClass("syscall_exit_%s" % name)
            sys_exit_event_class.add_field(uint64_type, "ret")
            stream_class.add_event_class(sys_entry_event_class)
            stream_class.add_event_class(sys_exit_event_class)
            event_classes["syscall_entry_%s" % name] = sys_entry_event_class
            event_classes["syscall_exit_%s" % name] = sys_exit_event_class
    else:
        # add this field declaration to event class
        func_entry_event_class = btw.EventClass(FUNC_ENTRY_EVENT_NAME)
        func_entry_event_class.add_field(uint64_type, ADDR_FIELD_NAME)
        func_entry_event_class.add_field(uint32_type, VTID_FIELD_NAME)
        func_entry_event_class.add_field(uint32_type, VPID_FIELD_NAME)
        func_entry_event_class.add_field(string_type, PROCNAME_FIELD_NAME)
        stream_class.add_event_class(func_entry_event_class)
        event_classes[FUNC_ENTRY_EVENT_NAME] = func_entry_event_class

        func_exit_event_class = btw.EventClass(FUNC_EXIT_EVENT_NAME)
        func_exit_event_class.add_field(uint64_type, ADDR_FIELD_NAME)
        func_exit_event_class.add_field(int32_type, VTID_FIELD_NAME)
        func_exit_event_class.add_field(int32_type, VPID_FIELD_NAME)
        func_exit_event_class.add_field(string_type, PROCNAME_FIELD_NAME)
        stream_class.add_event_class(func_exit_event_class)
        event_classes[FUNC_EXIT_EVENT_NAME] = func_exit_event_class

    if stream_name not in per_cpu_streams:
        per_cpu_streams[stream_name] = []

    for i in range(0, cpu_count):
        stream = writer.create_stream(stream_class)
        stream.packet_context.field("cpu_id").value = i
        per_cpu_streams[stream_name].append(stream)

    return event_classes


def main(argv):
    path = "/home/abder/lttng-traces/full-bootup-tracing-20170920-172556"
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

    kernel_symbols_path = os.path.join(path, "mapping/kallsyms.map")
    kernel_symbols_l1_path = os.path.join(path, "mapping/kallsyms-l1.map")
    process_symbols_l1_path = os.path.join(path, "mapping/process-l1.map")

    # Create TraceCollection and add trace:
    kernel_symbols = Symbols(kernel_symbols_path)
    kernel_symbols_l1 = Symbols(kernel_symbols_l1_path)
    process_symbols_l1 = Process(process_symbols_l1_path)
    hash_table = HashTable(kernel_symbols_path)
    process_list = Process("./script/process.txt")

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    print("--- Converting traces ---")

    # temporary directory holding the CTF trace
    trace_path = "%s-converted" % (path)
    print(trace_path)
    os.system('mkdir -p ' + trace_path+'/mapping')
    os.system('cp ' + os.path.join(path, "mapping/kallsyms*") + ' ' + trace_path+'/mapping')
    # our writers

    kernel_event_classes = {}
    ust_event_classes = {}

    kernel_event_classes['guest'] = create_writer("guest-kernel", trace_path)
    # kernel_event_classes['host'] = create_writer("host-kernel", trace_path)
    # ust_event_classes['host'] = create_writer("host-ust", trace_path)
    # ust_event_classes['guest'] = create_writer("guest-ust", trace_path)

    count = 0
    for event in traces.events:
        cpu_id = event['cpu_id']
        is_guest_event = is_hypercall_event(event.name)
        layer = "guest" if is_guest_event else "host"
        event_obj = None
        if is_guest_event:
            event_obj = handle_l1_event(event)
            if isinstance(event_obj, EventFunction):
                if process_symbols_l1.get_name(event_obj.tid) is not None:
                    event_obj.procname = "Guest: " + process_symbols_l1.get_name(event_obj.tid)
                name = hash_table.get_name(event_obj.hash_code)
                if name is None:
                    name = kernel_symbols_l1.get_name(event_obj.address)
                event_obj.function_name = kernel_symbols_l1.get_name(event_obj.address)
                # quick hack to use only one kallsyms file : Convert guest addr to host addr
                # if kernel_symbols.get_addr(event_obj.function_name) :
                #     event_obj.address = kernel_symbols.get_addr(event_obj.function_name)

        else:
            event_obj = handle_l0_event(event)
            if isinstance(event_obj, EventFunction):
                # print(event_obj.virt_level, kernel_symbols.get_name(event_obj.address), hash_table.get_name(event_obj.hash_code))
                event_obj.function_name = kernel_symbols.get_name(event_obj.address)

        if event_obj is None:
            continue

        is_ust = isinstance(event_obj, EventFunction)
        mode = "ust" if is_ust else "kernel"
        stream_name = layer + '-' + mode

        # if isinstance(event_obj, FunctionEntryExit) and event_obj.cpu_id != 0:
        #     continue
        if is_ust:
            sys_event_class = syscalls_event_class[layer]
            func_entry_class = function_event_class[layer][0]
            func_exit_class = function_event_class[layer][1]
            if isinstance(event_obj, FunctionEntry):
                entry_event = btw.Event(func_entry_class)
                entry_event.clock().time = event_obj.timestamp
                entry_event.payload(ADDR_FIELD_NAME).value = event_obj.address
                entry_event.payload(VTID_FIELD_NAME).value = event_obj.tid
                entry_event.payload(VPID_FIELD_NAME).value = event_obj.pid
                entry_event.payload(PROCNAME_FIELD_NAME).value = event_obj.procname
                per_cpu_streams[stream_name][event_obj.cpu_id].append_event(entry_event)
                # handle syscall entry
                if event_obj.function_name.lower().startswith("sys_"):
                    # print("cpu=%s, %s" % (event_obj.cpu_id,event_obj.function_name))
                    if event_obj.function_name.lower() in sys_event_class:
                        event_class = sys_event_class[event_obj.function_name.lower()]['syscall_entry']
                        syscall_event_entry = btw.Event(event_class)
                        syscall_event_entry.clock().time = event_obj.timestamp
                        name = "guest-kernel" if is_guest_event else "host-kernel"
                        per_cpu_streams[name][event_obj.cpu_id].append_event(syscall_event_entry)

            if isinstance(event_obj, FunctionExit):
                if event_obj.depth == 0:
                    count += 1
                    print(count)
                exit_event = btw.Event(func_exit_class)
                exit_event.clock().time = event_obj.timestamp
                exit_event.payload(ADDR_FIELD_NAME).value = event_obj.address
                exit_event.payload(VTID_FIELD_NAME).value = event_obj.tid
                exit_event.payload(VPID_FIELD_NAME).value = event_obj.pid
                exit_event.payload(PROCNAME_FIELD_NAME).value = event_obj.procname
                per_cpu_streams[stream_name][event_obj.cpu_id].append_event(exit_event)
                # handle syscall exit
                if event_obj.function_name.lower().startswith("sys_"):
                    if event_obj.function_name.lower() in sys_event_class:
                        event_class = sys_event_class[event_obj.function_name.lower()]['syscall_exit']
                        syscall_event_exit = btw.Event(event_class)
                        syscall_event_exit.clock().time = event_obj.timestamp
                        name = "guest-kernel" if is_guest_event else "host-kernel"
                        per_cpu_streams[name][event_obj.cpu_id].append_event(syscall_event_exit)

        elif isinstance(event_obj, dict):
            event_classes = kernel_event_classes[layer]
            event_class = event_classes[event_obj['type']]
            payload = event_obj["payload"]
            new_event = btw.Event(event_class)
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
        count += 1
        if count > 10000:
            break
    # flush the streams

    for domain, streams in per_cpu_streams.items():
        print("%s flushing streams" % domain)
        for i in range(0, len(streams)):
            streams[i].flush()


if __name__ == "__main__":
    main(sys.argv[1:])

