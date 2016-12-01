set -x

lttng create bootup-tracing
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel

lttng enable-event -k "sched_*,kvm_x86_hypercall" -c vm_channel

lttng start

ssh root@ubuntu 'echo function_graph > /sys/kernel/debug/tracing/current_tracer'
ssh root@ubuntu 'echo 1 > /sys/kernel/debug/tracing/tracing_on'
sleep 5
ssh root@ubuntu 'echo 0 > /sys/kernel/debug/tracing/tracing_on'

lttng stop
#lttng view
lttng destroy

