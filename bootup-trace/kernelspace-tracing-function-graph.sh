#!/usr/bin/env bash
set -x

ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
ssh root@ubuntu 'echo do_sys_open > /sys/kernel/debug/tracing/set_graph_function'
ssh root@ubuntu 'echo nop > /sys/kernel/debug/tracing/current_tracer'
#ssh root@ubuntu 'echo funcgraph-proc > /sys/kernel/debug/tracing/trace_options'


lttng create function-graph
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel
#lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k -a -c vm_channel
lttng start
#ssh ubuntu 'sudo insmod ~/fgraph/fgraph.ko; ./simple-program-ins-dohypercall; sudo rmmod fgraph;'

ssh root@ubuntu 'echo function_graph > /sys/kernel/debug/tracing/current_tracer'
ssh root@ubuntu 'echo funcgraph-proc > /sys/kernel/debug/tracing/trace_options'
ssh root@ubuntu 'echo funcgraph-irqs > /sys/kernel/debug/tracing/trace_options'
ssh root@ubuntu 'echo 1 > /sys/kernel/debug/tracing/tracing_on;sleep 0.01;echo 0 > /sys/kernel/debug/tracing/tracing_on;'
#ssh ubuntu '~/simple-program-ins-dohypercall'

#ssh root@ubuntu '
#echo 1 > /sys/kernel/debug/tracing/tracing_on;
#/home/abder/simple-program-ins-dohypercall;
#echo 0 > /sys/kernel/debug/tracing/tracing_on;'
#sleep 1;
lttng stop
lttng destroy

ssh ubuntu "nm -an simple-program-ins-dohypercall > program-symbols.txt"
scp ubuntu:~/program-symbols.txt .
ssh root@ubuntu "cat /debug/tracing/trace" > ./logs/trace-function-graph.txt
./dump-symbols.sh
