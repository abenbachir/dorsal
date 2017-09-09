#!/usr/bin/env bash
# set -x
#virsh vcpupin VM 0 1
# virsh vcpuinfo VM
target_l1=ubuntu2
target_l2=nested-vm2
trace_dir="/home/abder/lttng-traces/tracers/syscall"

ftrace_notrace="
echo global > /sys/kernel/debug/tracing/trace_clock;
echo > /sys/kernel/debug/tracing/set_ftrace_filter;
echo note_page > /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *kmem_cache* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *slab* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *acpi* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo _raw_spin_* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *mutex* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *mutex* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo _cond_resched >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *console* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *fb* >> /sys/kernel/debug/tracing/set_ftrace_notrace;"

start_host_tracing() {
    output=$1
    lttng create hypergraph
    lttng enable-channel -k --subbuf-size=64K --num-subbuf=1024 vm_channel
    lttng enable-event -k "sched_switch" -c vm_channel
    lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
    lttng enable-event -k "func_entry,func_exit,func_entry_exit" --filter '$ctx.cpu_id == 0' -c vm_channel
    lttng add-context -k -t pid -t tid -t procname
#    sudo insmod /home/abder/lttng/lttng-modules/probes/lttng-fgraph.ko
    lttng start
}
stop_host_tracing() {
    lttng stop
    lttng view | wc -l
    lttng destroy
#    sudo rmmod lttng-fgraph
}
#note_page,*kmem_cache*,*slab*,*acpi*,_raw_spin_*,*mutex*,_cond_resched,*console*,*fb*
setup_l0_ftrace()
{
    ssh root@localhost "$ftrace_notrace
    echo global > /sys/kernel/debug/tracing/trace_clock;"
}
setup_l1_ftrace()
{
    ssh root@$target_l1 "echo 0 > /sys/kernel/debug/tracing/tracing_on;
        $ftrace_notrace
    	echo hypergraph > /sys/kernel/debug/tracing/current_tracer;
        echo > /sys/kernel/debug/tracing/trace;
        echo global > /sys/kernel/debug/tracing/trace_clock"

}

setup_l2_ftrace()
{
    ssh root@$target_l1 "ssh root@$target_l2 'echo 0 > /sys/kernel/debug/tracing/tracing_on;
        $ftrace_notrace
    	echo hypergraph > /sys/kernel/debug/tracing/current_tracer;
        echo > /sys/kernel/debug/tracing/trace;
        echo global > /sys/kernel/debug/tracing/trace_clock'"
}


hypergraph_tracing()
{
    CMD=$1
    setup_l0_ftrace
    setup_l1_ftrace
#    setup_l2_ftrace

#    ssh root@$target_l1 "echo 1 > /sys/kernel/debug/tracing/tracing_on"
    start_host_tracing
#    sudo insmod /home/abder/lttng/lttng-modules/probes/lttng-fgraph.ko

    ssh root@$target_l1 "echo 1 > /sys/kernel/debug/tracing/tracing_on &&
     $CMD &&
     echo 0 > /sys/kernel/debug/tracing/tracing_on"

#    ssh root@$target_l1 "sudo trace-cmd record -p hypergraph $CMD"
    sleep 0.1
    stop_host_tracing

#    sudo rmmod lttng-fgraph
#    ssh root@$target_l1 "echo 0 > /sys/kernel/debug/tracing/tracing_on"
}


cmd="echo 'test'"
hypergraph_tracing "${cmd}"