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


class Dmesg:
    def __init__(self, filepath, offset):
        self.filepath = filepath
        self.logs = {}
        self.offset = offset
        if not os.path.exists(filepath):
            return
        i, time = 0, 0
        with open(filepath) as f:
            lines = f.readlines()
            while i < len(lines):
                line = lines[i]
                try:
                    arg1, arg2 = line[0:14], line[15:-1]
                    is_time = arg1.startswith('[') and arg1.endswith(']')
                    if not is_time:
                        start_time = time + 300
                        end_time = start_time + 100
                        sub_content = line
                        j = i + 1
                        while j < len(lines):
                            sub_line = lines[j]
                            sub_arg1, sub_arg2 = sub_line[0:14], sub_line[15:-1]

                            is_time = sub_arg1.startswith('[') and sub_arg1.endswith(']')
                            if not is_time:
                                sub_content += sub_line
                            else:
                                end_time = int(float(sub_arg1.lstrip('[').lstrip('>[').rstrip(']').strip(' ')) * 10**9) - 300
                                break
                            j += 1
                        log = {
                            'time': start_time,
                            'start': start_time+offset,
                            'end': end_time + offset,
                            'content': sub_content,
                            'cat':'_stdout'
                        }
                        self.logs[start_time] = log
                        i = j - 1
                    else:
                        time = int(float(arg1.lstrip('[').lstrip('>[').rstrip(']').strip(' ')) * 10**9)
                        content = arg2.strip(' ')
                        timestamp = offset + time
                        log = {
                            'time': time,
                            'start': timestamp,
                            'end': timestamp+100,
                            'content': content,
                            'cat': '_logs'
                        }
                        self.logs[time] = log
                except Exception as ex:
                    print(ex)
                finally:
                    i += 1



def main(argv):
    path = "/home/abder/lttng-traces/oneos-boot-vm7_ps1/"
    output = None
    try:
        if len(argv) > 0:
            path = argv[0]
            # kernel_symbols_path = argv[1]
    except Exception as ex:
        if not path:
            raise TypeError(HELP)

    path = path.rstrip('/')
    dmesg_path = os.path.join(path, "mapping/session.log")
    # timestamp of first hypercall - time when Starting tracer 'hypertrace'
    offset = 1506612632172639999-24113000
    dmesg = Dmesg(dmesg_path, offset)

    trace_path = "%s-converted" % (path)
    print(trace_path)
    stream_name = 'dmesg'
    writer = btw.Writer(os.path.join(trace_path, stream_name))
    clock = btw.Clock('monotonic')
    writer.add_clock(clock)
    writer.add_environment_field("domain", 'kernel')
    writer.add_environment_field("tracer_name", "lttng-modules")
    writer.add_environment_field("tracer_major", 2)
    writer.add_environment_field("tracer_minor", 10)
    stream_class = btw.StreamClass('channel')
    stream_class.clock = clock

    packet_context_type = stream_class.packet_context_type
    packet_context_type.add_field(uint32_type, "cpu_id")
    stream_class.packet_context_type = packet_context_type
    # marker events
    marker_event_class = btw.EventClass(MARKER_EVENT_NAME)
    marker_event_class.add_field(int64_type, "start")
    marker_event_class.add_field(int64_type, "end")
    marker_event_class.add_field(string_type, "category")
    marker_event_class.add_field(string_type, "label")
    marker_event_class.add_field(string_type, "description")
    stream_class.add_event_class(marker_event_class)
    stream = writer.create_stream(stream_class)
    stream.packet_context.field("cpu_id").value = 0

    for time, log in sorted(dmesg.logs.items()):
        try:
            time = log['time']
            content = log['content']

            log_event = btw.Event(marker_event_class)
            log_event.clock().time = log['start']
            log_event.payload('label').value = content[0:20]
            log_event.payload('category').value = log['cat']
            log_event.payload('description').value = content
            log_event.payload('start').value = log['start']
            log_event.payload('end').value = log['end']
            stream.append_event(log_event)
            print(time)
        except Exception as ex:
            print(log, ex)

    stream.flush()

if __name__ == "__main__":
    main(sys.argv[1:])

