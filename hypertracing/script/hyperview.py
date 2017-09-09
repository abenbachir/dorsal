#!/usr/bin/python3

import getopt
import sys
import os
import babeltrace.reader
from utils import *

HEADER = """tracer: hypergraph

CPU  TASK/PID      DURATION      Depth         FUNCTION CALLS
 |    |    |         |   |         |           |   |   |   |"""
# tracer: function_graph
#
# CPU  TASK/PID         DURATION     Depth         FUNCTION CALLS
# |     |    |           |   |         |           |   |   |   |
#  7)   bash-21261   |   0.111 us    |  d=1  |  mutex_unlock();
#  5)   <->-0        | 0.674 us      | d=1  |


def main(argv):
    path = ""
    kernel_symbols_path = "./script/kallsyms.map"
    input_word = ""
    input_cpuid = ""
    input_pid = ""

    try:
        path = argv[0]
        if len(argv) > 0:
            kernel_symbols_path = argv[1]
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
    
    # Create TraceCollection and add trace:
    kernel_symbols = Symbols(kernel_symbols_path)
    hash_table = HashTable(kernel_symbols_path)
    process_list = Process("./script/process.txt")

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    print(HEADER)
    start_timestamp = 0
    event_obj = ""
    for event in traces.events:

        if is_hypercall_event(event.name):
            event_obj = handle_l1_event(event)
        else:
            event_obj = handle_l0_event(event)
        print(event_obj)


if __name__ == "__main__":
    main(sys.argv[1:])

"""
do_one_initcall 3222275001
kallsyms_lookup 3223023465

"""
