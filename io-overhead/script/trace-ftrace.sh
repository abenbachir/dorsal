#!/usr/bin/env bash
# set -x

lttng create trace-ftrace
lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
lttng enable-event -k sched_switch,lttng_statedump* -c vm_channel
lttng enable-event -k --syscall open,write,read,close,fork,clone -c vm_channel
lttng add-context -k -t pid -t tid -t procname

echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo funcgraph-proc >  /sys/kernel/debug/tracing/trace_options
echo > /sys/kernel/debug/tracing/trace

lttng start
echo 1 > /sys/kernel/debug/tracing/tracing_on && sleep 1 && echo 0 > /sys/kernel/debug/tracing/tracing_on
lttng stop

lttng view | wc -l
lttng destroy