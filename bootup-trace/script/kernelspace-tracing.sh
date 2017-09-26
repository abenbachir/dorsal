#!/usr/bin/env bash
set -x
target=ubuntu2

#ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
ssh root@$target 'echo > /sys/kernel/debug/tracing/set_ftrace_filter'
ssh root@$target 'echo > /sys/kernel/debug/tracing/set_ftrace_notrace'
ssh root@$target 'echo > /sys/kernel/debug/tracing/set_graph_function'
ssh root@$target 'echo > /sys/kernel/debug/tracing/set_graph_notrace'
ssh root@$target 'echo nop > /sys/kernel/debug/tracing/current_tracer'

lttng create hypergraph
lttng enable-channel -k --subbuf-size=128K --num-subbuf=32 vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
#lttng enable-event -k -a -c vm_channel
lttng start
#ssh $target 'sudo insmod ~/fgraph/fgraph.ko; ./simple-program-ins-dohypercall; sudo rmmod fgraph;'

ssh root@$target 'echo hypergraph > /sys/kernel/debug/tracing/current_tracer'
#ssh root@$target 'echo 0 > /sys/kernel/debug/tracing/max_hypergraph_depth'
ssh root@$target 'echo 1 > /sys/kernel/debug/tracing/tracing_on; sleep 0.01; echo 0 > /sys/kernel/debug/tracing/tracing_on'

#ssh $target '~/simple-program-ins-dohypercall'
#ssh root@$target 'echo 0 > /sys/kernel/debug/tracing/tracing_on'


lttng stop
lttng destroy

./script/dump-symbols.sh

