#!/usr/bin/env bash

target=vm
trace_dir="/home/abder/lttng-traces/hypertracing/cpu"
drop_cache='free && sync && echo 1 > /proc/sys/vm/drop_caches && sync && echo 2 > /proc/sys/vm/drop_caches && sync && echo 3 > /proc/sys/vm/drop_caches && free'
swapoff='swapoff -a && swapon -a'

start_host_tracing() {
    output=$1
    lttng create hypertracing --output="$output"
    lttng enable-channel -k --subbuf-size=8M --num-subbuf=128 vm_channel
    lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel
    lttng start
}
stop_host_tracing() {
    lttng stop
    lttng view | wc -l
    lttng destroy
}
no_workload()
{
    nthreads=$1
    maxprime=$2
    CMD=$3
    output="$trace_dir/non/l1-cpu_benchmark-no_workload-${nthreads}_${maxprime}-$(dbus-uuidgen)"
    start_host_tracing "${output}"
    ssh root@vm "$drop_cache && ./hypertime && ./hypertime end && free"
    stop_host_tracing
}

no_tracing()
{
    nthreads=$1
    maxprime=$2
    CMD=$3
    output="$trace_dir/non/l1-cpu_benchmark-none-${nthreads}_${maxprime}-$(dbus-uuidgen)"
    start_host_tracing "${output}"

    ssh root@$target "$drop_cache && ./hypertime && $CMD && ./hypertime end"

    stop_host_tracing
}

lttng_tracing()
{
    nthreads=$1
    maxprime=$2
    CMD=$3
    output="$trace_dir/lttng/l1-cpu_benchmark-lttng-${nthreads}_${maxprime}-$(dbus-uuidgen)"

    ssh root@$target 'rm -rf lttng-traces/*;
        lttng create cpu-traces;
        lttng enable-channel -k vm_channel;
        lttng enable-event -k sched_switch,sched_migrate_task,sched_process_fork,sched_process_exit -c vm_channel'

    start_host_tracing "${output}"

    ssh root@$target "$drop_cache && lttng start && ./hypertime && $CMD && ./hypertime end && lttng stop; lttng view | wc -l;echo \"collected events\";lttng destroy"

    stop_host_tracing
}

ftrace_tracing()
{
    nthreads=$1
    maxprime=$2
    CMD=$3
    output="$trace_dir/ftrace/l1-cpu_benchmark-ftrace-${nthreads}_${maxprime}-$(dbus-uuidgen)"

    ssh root@$target 'echo nop > /sys/kernel/debug/tracing/current_tracer;
        echo > /sys/kernel/debug/tracing/trace;
        echo 1 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable;
        echo 1 > /sys/kernel/debug/tracing/events/sched/sched_migrate_task/enable;
        echo 1 > /sys/kernel/debug/tracing/events/sched/sched_process_fork/enable;
        echo 1 > /sys/kernel/debug/tracing/events/sched/sched_process_exit/enable;'

    start_host_tracing "${output}"

    ssh root@$target "$drop_cache &&
    echo 1 > /sys/kernel/debug/tracing/tracing_on &&
    ./hypertime && $CMD && ./hypertime end &&
    echo 0 > /sys/kernel/debug/tracing/tracing_on;
    head -n 3 /sys/kernel/debug/tracing/trace"

    stop_host_tracing
}

perf_tracing()
{
    nthreads=$1
    maxprime=$2
    CMD=$3
    output="$trace_dir/perf/l1-cpu_benchmark-perf-${nthreads}_${maxprime}-$(dbus-uuidgen)"

    start_host_tracing "${output}"

    perf_cmd="sudo perf record -e 'sched:sched_switch,sched:sched_migrate_task,sched:sched_process_fork,sched:sched_process_exit' -a $CMD > /dev/null"
    ssh root@$target "$drop_cache && ./hypertime && $perf_cmd && ./hypertime end"

    stop_host_tracing
    ssh root@$target "sudo pkill perf; sudo rm perf.data"
}



for nthreads in 1 2 4
do
    worload="sysbench"
    maxprime=10000
    cmd="sysbench --test=cpu --num-threads=${nthreads} --cpu-max-prime=${maxprime} run"

#    for i in {1..50}
#        do
#        echo "Preparing benchmark"; sleep 1
#        no_tracing "${nthreads}" "${maxprime}" "${cmd}"
#    done
#
#    for i in {1..5}
#        do
#        echo "Preparing benchmark"; sleep 1
#        lttng_tracing "${nthreads}" "${maxprime}" "${cmd}"
#    done
#
#    for i in {1..50}
#        do
#        echo "Preparing benchmark"; sleep 1
#        perf_tracing "${nthreads}" "${maxprime}" "${cmd}"
#    done

    for i in {1..50}
        do
        echo "Preparing benchmark"; sleep 1
        ftrace_tracing "${nthreads}" "${maxprime}" "${cmd}"
    done

    echo ""
done