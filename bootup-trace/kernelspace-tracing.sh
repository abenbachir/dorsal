#!/usr/bin/env bash
set -x

#ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
ssh root@ubuntu 'echo > /sys/kernel/debug/tracing/set_ftrace_filter'
ssh root@ubuntu 'echo > /sys/kernel/debug/tracing/set_ftrace_notrace'
ssh root@ubuntu 'echo > /sys/kernel/debug/tracing/set_graph_function'
ssh root@ubuntu 'echo > /sys/kernel/debug/tracing/set_graph_notrace'
ssh root@ubuntu 'echo nop > /sys/kernel/debug/tracing/current_tracer'

lttng create hypergraph
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
#lttng enable-event -k -a -c vm_channel
lttng start
#ssh ubuntu 'sudo insmod ~/fgraph/fgraph.ko; ./simple-program-ins-dohypercall; sudo rmmod fgraph;'

ssh root@ubuntu 'echo hypergraph > /sys/kernel/debug/tracing/current_tracer'
ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/max_hypergraph_depth'
ssh root@ubuntu 'echo 1 > /sys/kernel/debug/tracing/tracing_on; sleep 0.01; echo 0 > /sys/kernel/debug/tracing/tracing_on'
sleep
#ssh ubuntu '~/simple-program-ins-dohypercall'
#ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/tracing_on'


lttng stop
lttng destroy

ssh ubuntu "nm -an simple-program-ins-dohypercall > program-symbols.txt"
scp ubuntu:~/program-symbols.txt ./logs/
./dump-symbols.sh

