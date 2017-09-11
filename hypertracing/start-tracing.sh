#!/usr/bin/env bash
# set -x

# virsh vcpuinfo VM
target_l1=vm1
target_l2=nested-vm2
max_depth=2
trace_dir="/home/abder/lttng-traces/tracers/syscall"

virsh vcpupin $target_l1 0 0

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
echo *fb* >> /sys/kernel/debug/tracing/set_ftrace_notrace;
echo *kfree* >> /sys/kernel/debug/tracing/set_ftrace_notrace"

start_host_tracing() {
    output=$1
    lttng create hypergraph --output=/home/abder/lttng-traces/hypergraph
    lttng enable-channel -k --subbuf-size=256K --num-subbuf=512 vm_channel
    lttng enable-event -k "sched_switch" -c vm_channel
   # lttng enable-event -k --syscall -a -c vm_channel
    lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
     lttng enable-event -k "func_entry,func_exit,func_entry_exit" --filter '$ctx.cpu_id == 0' -c vm_channel
    # lttng enable-event -k "func_entry,func_exit,func_entry_exit" -c vm_channel
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
    ssh root@localhost "$ftrace_notrace"
}
setup_l1_ftrace()
{
    ssh root@$target_l1 "echo 0 > /sys/kernel/debug/tracing/tracing_on;
        $ftrace_notrace
    	echo hypergraph > /sys/kernel/debug/tracing/current_tracer"

}

setup_l2_ftrace()
{
    ssh root@$target_l1 "ssh root@$target_l2 'echo 0 > /sys/kernel/debug/tracing/tracing_on;
        $ftrace_notrace
    	echo hypergraph > /sys/kernel/debug/tracing/current_tracer'"
}

dump_symbols()
{
    sudo cat /proc/kallsyms > script/kallsyms.map
    ssh $target_l1 "sudo cat /proc/kallsyms" > script/kallsyms-l1.map
#    ssh $target_l1 "ssh $target_l2 'sudo cat /proc/kallsyms'" > script/kallsyms-l1.map

}
hypergraph_tracing()
{
    CMD=$1
    setup_l0_ftrace
    setup_l1_ftrace
#    setup_l2_ftrace

    start_host_tracing

    echo 1 > /proc/lttng-fgraph

    ssh root@$target_l1 "echo 1 > /sys/kernel/debug/tracing/tracing_on &&
     $CMD && echo 0 > /sys/kernel/debug/tracing/tracing_on"
    
    # sudo cat /proc/kallsyms > script/kallsyms.map
    # cat /proc/cpuinfo > /tmp/test.txt

    echo 0 > /proc/lttng-fgraph

    stop_host_tracing

    cat /proc/lttng-fgraph
    dump_symbols
}


cmd="cat /proc/cpuinfo > /tmp/test.txt"
hypergraph_tracing "${cmd}"

./script/babeltrace_to_ctf.py /home/abder/lttng-traces/hypergraph