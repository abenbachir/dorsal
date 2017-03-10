#!/usr/bin/env bash
set -x

ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/tracing_on'

ssh root@ubuntu 'echo nop > /sys/kernel/debug/tracing/current_tracer'

lttng create function
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
lttng start

ssh root@ubuntu 'echo function > /sys/kernel/debug/tracing/current_tracer'
ssh root@ubuntu 'echo 1 > /sys/kernel/debug/tracing/tracing_on;sleep 0.05;echo 0 > /sys/kernel/debug/tracing/tracing_on;'

#ssh ubuntu '~/simple-program-ins-dohypercall'

lttng stop
lttng destroy


ssh ubuntu "sudo cat /proc/kallsyms > symbols.txt"
scp ubuntu:~/symbols.txt .
ssh root@ubuntu "cat /debug/tracing/trace" > trace.txt
