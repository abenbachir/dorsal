#!/usr/bin/python3

import getopt
import sys
import os
import operator
import babeltrace.reader


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

def main(argv):
    path = "/home/abder/lttng-traces/block-io-traces-20170811-121042"
    filters = []
    try:
        path = argv[0]
        if len(argv) > 1:
            filters = argv[1].split(',')
    except Exception as ex:
        if not path:
            raise TypeError()

    traces = babeltrace.reader.TraceCollection()
    trace_handle = traces.add_traces_recursive(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    threads = dict()
    for event in traces.events:
        fields = dict()
        for k, v in event.items():
            field_type = event._field(k).type
            fields[k] = format_value(field_type, v)

        cpu_id = event['cpu_id']
        timestamp = event.timestamp

        # Handle hypercall (sched_switch)
        if event.name == "sched_switch":
            prev_comm = "".join(fields['prev_comm'])
            prev_tid = fields['prev_tid']
            next_comm = "".join(fields['next_comm'])
            next_tid = fields['next_tid']
            threads[prev_tid] = prev_comm
            threads[next_tid] = next_comm

        if event.name == "block_rq_insert":
            comm = "".join(fields['comm'])
            tid = fields['tid']
            if 'pid' in fields:
                pid = fields['pid']
                threads[pid] = comm
            threads[tid] = comm


    # Printing
    if filters:
        filtered_threads = {}
        for tid, thread_name in threads.items():
            for filter in filters:
                if filter.lower() in thread_name.lower():
                    if filter not in filtered_threads:
                        filtered_threads[filter] = []
                    filtered_threads[filter].append(tid)
        print(filtered_threads)
    else:
        print(threads)
    # for tid, thread_name in threads.items():
    #     # if tid != 19388:
    #     #     continue
    #     print('%s-%s'%(tid,thread_name))

if __name__ == "__main__":
    main(sys.argv[1:])