#!/usr/bin/env bash

#virsh vcpupin VM 0 1
virsh vcpuinfo VM
target=vm
trace_dir="/home/abder/lttng-traces/tracers/sched"
drop_cache='free && sync && echo 1 > /proc/sys/vm/drop_caches && sync && echo 2 > /proc/sys/vm/drop_caches && sync && echo 3 > /proc/sys/vm/drop_caches && free'
swapoff='swapoff -a && swapon -a'
limiter="======================================================"

reset(){
    ssh $target 'sudo pkill lttng; pgrep lttng -l'
    ssh root@$target 'echo nop > /sys/kernel/debug/tracing/current_tracer;echo 0 > /sys/kernel/debug/tracing/events/enable'
    ssh root@$target "$drop_cache"
}
start_host_tracing_snapshot() {
    output=$1
    lttng create host-traces --output="$output" --snapshot
    lttng enable-channel -k --subbuf-size=8K --num-subbuf=32 vm_channel
    lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
    lttng start
}
stop_host_tracing_snapshot() {
    arg=0
    lttng stop
    lttng snapshot record --name=kernel
    lttng destroy
}
start_host_tracing() {
    output=$1
    lttng create host-traces --output="$output"
    lttng enable-channel -k --subbuf-size=32K --num-subbuf=32 vm_channel
    lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
#    lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel
    lttng start
}
stop_host_tracing() {
    arg=0
    lttng stop
    lttng view | wc -l
    lttng destroy
}

no_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/none/l1-sched_benchmark-none-${workload}-$(dbus-uuidgen)"
    start_host_tracing "${output}"

    ssh $target "$CMD"

    stop_host_tracing
}

hypertracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/hypertracing/l1-sched_benchmark-hyperT-${workload}-$(dbus-uuidgen)"

    ssh $target 'sudo insmod hypertracing/sched_hypertracing_guest.ko'

    start_host_tracing "${output}"

    ssh $target "$CMD"

    stop_host_tracing
    ssh $target 'sudo rmmod sched_hypertracing_guest'
}



lttng_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/lttng/l1-sched_benchmark-lttng-${workload}-$(dbus-uuidgen)"

    ssh $target 'rm -rf lttng-traces/*;
        lttng create sched-traces;
        lttng enable-channel -k --subbuf-size=16K --num-subbuf=32 vm_channel;
        lttng enable-event -k sched_switch -c vm_channel'

    start_host_tracing "${output}"

    ssh $target "lttng start && $CMD && lttng stop; lttng view | wc -l;echo \"collected events\";lttng destroy"

    stop_host_tracing
}

ftrace_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/ftrace/l1-sched_benchmark-ftrace-${workload}-$(dbus-uuidgen)"

    ssh root@$target 'echo nop > /sys/kernel/debug/tracing/current_tracer;
        echo > /sys/kernel/debug/tracing/trace;
        echo 400 > /sys/kernel/debug/tracing/buffer_size_kb;
        echo 1 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable'

    start_host_tracing "${output}"

    ssh root@$target "echo 1 > /sys/kernel/debug/tracing/tracing_on &&
    $CMD && echo 0 > /sys/kernel/debug/tracing/tracing_on;
    head -n 3 /sys/kernel/debug/tracing/trace"

    stop_host_tracing
}

perf_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/perf/l1-sched_benchmark-perf-${workload}-$(dbus-uuidgen)"

    start_host_tracing "${output}"

    ssh $target "sudo perf record -e 'sched:sched_switch' -a $CMD > /dev/null"

    stop_host_tracing
    ssh $target "sudo pkill perf; sudo rm perf.data*"
}

hypertracing_compress()
{
    workload=$1
    CMD=$2
    output="$trace_dir/hypertracing/l1-sched_benchmark-hyperT_compress_5-${workload}-$(dbus-uuidgen)"

    ssh $target 'sudo insmod hypertracing/sched_hypertracing_compress_guest.ko'

    start_host_tracing "${output}"

    ssh $target "$CMD"

    stop_host_tracing
    ssh $target 'sudo rmmod sched_hypertracing_compress_guest'
}

threads=2
events=1000
#events=10000
workload="sched_switch_${threads}_${events}"
cmd="./sched-switch-micro-benchmark ${threads} ${events}"

repeat=30

#reset
#echo "$limiter None $limiter";
#for i in $(eval echo "{1..$repeat}")
#    do
#    no_tracing "${workload}" "${cmd}"
#done
#
#reset
#echo "$limiter Hypertracing $limiter"
#for i in $(eval echo "{1..$repeat}")
#    do
#    sleep 0.1
#    hypertracing "${workload}" "${cmd}"
#done
#
#reset
#echo "$limiter Perf $limiter"
#for i in $(eval echo "{1..$repeat}")
#    do
#    sleep 0.1
#    perf_tracing "${workload}" "${cmd}"
#done
#
reset
echo "$limiter Ftrace $limiter"
for i in $(eval echo "{1..$repeat}")
    do
    sleep 0.1
    ftrace_tracing "${workload}" "${cmd}"
done
ssh root@$target 'echo nop > /sys/kernel/debug/tracing/current_tracer;echo 0 > /sys/kernel/debug/tracing/events/enable'
#
#
#reset
#echo "$limiter Lttng $limiter"
#ssh $target 'sudo lttng-sessiond -d; pgrep lttng -l'
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    lttng_tracing "${workload}" "${cmd}"
#done
#ssh $target 'sudo pkill lttng; pgrep lttng -l'

#reset
#echo "$limiter Hypertracing compress $limiter"
#for i in $(eval echo "{1..$repeat}")
#    do
#    sleep 0.1
#    hypertracing_compress "${workload}" "${cmd}"
#done