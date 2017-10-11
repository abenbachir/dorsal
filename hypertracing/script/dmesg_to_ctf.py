#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.writer as btw
import babeltrace.reader
import re

try:
    from .utils import *
except Exception as ex:
    from utils import *

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
default_color = [0, 0, 0, 100]
colors = {
    'kmsg': [200, 200, 200, 100],
    'bootexec': [0, 0, 100, 100],
    'init': [0, 100, 0, 100]
}

def getColor(category):
    return toInt(*colors[category]) if category in colors else toInt(*default_color)

def toInt(r, g, b , a):
    return a << 24 | b << 16 | g << 8 | r

class Dmesg:

    def __init__(self, filepath, offset, time_drift):
        self.filepath = filepath
        self.logs = {}
        self.offset = offset
        self.time_drift = time_drift
        if not os.path.exists(filepath):
            print('File not found %s'%filepath)
            return
        i, time = 0, offset
        with open(filepath) as f:
            lines = f.readlines()
            while i < len(lines):
                line = lines[i]
                try:
                    category = 'kmsg'
                    matches = re.findall(r'\[(.*?)\]', line)
                    # print(matches)

                    is_time = line.startswith('[') and len(matches) > 0 and is_number(matches[0])
                    if not is_time:
                        start_time = time + 300
                        # end_time = start_time + 100
                        # sub_content = line
                        # j = i + 1
                        # while j < len(lines):
                        #     sub_line = lines[j]
                        #     sub_arg1, sub_arg2 = sub_line[0:14], sub_line[15::]
                        #
                        #     is_time = sub_arg1.startswith('[') and sub_arg1.endswith(']')
                        #     if not is_time:
                        #         sub_content += sub_line
                        #     else:
                        #         end_time = int(float(sub_arg1.lstrip('[').lstrip('>[').rstrip(']').strip(' ')) * 10**9) - 300
                        #         break
                        #     j += 1
                        # log = {
                        #     'time': start_time,
                        #     'start': start_time+offset,
                        #     'end': end_time + offset,
                        #     'content': sub_content,
                        #     'cat':'_stdout'
                        # }
                        # self.logs[start_time] = log
                        # i = j - 1
                    else:
                        arg1 = matches[0]
                        is_duration = len(arg1) == 12
                        arg2 = line[len(arg1)+2::].strip(' ').rstrip('\n')
                        time = float(arg1.strip(' '))
                        # if time == 0:
                        #     time = 100
                        matches2 = re.findall(r'<(.*?)>', arg2)
                        if len(matches2) > 0 and arg2.startswith('<'):
                            print(matches2)
                            category = matches2[0]
                            arg2 = arg2[len(matches2[0])+2::].strip(':').strip(' ')
                        elif arg2.startswith(':'):
                            continue

                        content = arg2
                        if content == "":
                            continue

                        timestamp = offset + (time * 10**9) if is_duration else time + time_drift
                        timestamp = int(timestamp)
                        log = {
                            'time': time,
                            'start': timestamp,
                            'end': timestamp+100,
                            'content': content,
                            'cat': category,
                            'color': getColor(category),
                            'is_duration': is_duration
                        }
                        self.logs[timestamp] = log
                except Exception as ex:
                    print(ex)
                finally:
                    i += 1


def main(argv):
    path = "/home/abder/lttng-traces/oneos-bootup/"
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
    host_start_tracing_ts = 1507051300.392043240 * 10**9
    guest_start_tracing_ts = 350887724 << 32 | 878125696
    guest_start_tracing_dur = 26417000
    time_drift = int(host_start_tracing_ts - guest_start_tracing_ts)
    offset = (guest_start_tracing_ts - guest_start_tracing_dur) + time_drift
    # offset -= 2 * 10**8
    dmesg = Dmesg(dmesg_path, offset, time_drift)

    trace_path = "%s/dmesg" % (path)
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
    marker_event_class.add_field(int32_type, "color")
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
            label = " ".join(content.split(' ')[0:3])
            log_event = btw.Event(marker_event_class)
            log_event.clock().time = log['start']
            log_event.payload('label').value = label
            log_event.payload('category').value = log['cat']
            log_event.payload('description').value = content
            log_event.payload('start').value = log['start']
            log_event.payload('end').value = log['end']
            log_event.payload('color').value = log['color']
            stream.append_event(log_event)
            # print(len(str(log['start'])),log['start'], log['start']-offset)
            print(log['cat'], ' | ', label, ' | ', content)
        except Exception as ex:
            print(log, ex)

    stream.flush()

if __name__ == "__main__":
    main(sys.argv[1:])

