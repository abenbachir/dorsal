#!/usr/bin/env bash
set -x
scp ubuntu:~/symbols.txt .

lttng create bootup-tracing
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel

lttng enable-event -k "sched_*,kvm_x86_hypercall" -c vm_channel

lttng start
$@
lttng stop
#lttng view
lttng destroy

scp ubuntu:~/bootup-logs.txt .