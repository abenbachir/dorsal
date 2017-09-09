#!/usr/bin/env bash

trace_dir="/home/abder/lttng-traces/tracers/syscall"
drop_cache='free && sync && echo 1 > /proc/sys/vm/drop_caches && sync && echo 2 > /proc/sys/vm/drop_caches && sync && echo 3 > /proc/sys/vm/drop_caches && free'
swapoff='swapoff -a && swapon -a'
limiter="======================================================"

reset(){
   echo nop > /sys/kernel/debug/tracing/current_tracer;echo 0 > /sys/kernel/debug/tracing/events/enable
   sudo $drop_cache
}

lttng_tracing_flight_recorder()
{
    workload=$1
    CMD=$2

    lttng create l0-syscall --snapshot
    lttng enable-channel -k --subbuf-size=8K --num-subbuf=2 vm_channel
    lttng enable-event -k --syscall getcpu -c vm_channel

    lttng start && $CMD && lttng stop
    lttng destroy

}

lttng_tracing()
{
    workload=$1
    CMD=$2

    lttng create l0-syscall
    lttng enable-channel -k --subbuf-size=128K --num-subbuf=512 vm_channel
    lttng enable-event -k --syscall getcpu -c vm_channel

    lttng start && $CMD && lttng stop
    lttng view | wc -l
    echo "collected events"
    lttng destroy
}

ftrace_tracing_flight_recorder()
{
    workload=$1
    CMD=$2

    echo nop > /sys/kernel/debug/tracing/current_tracer
    echo > /sys/kernel/debug/tracing/trace
    echo global > /sys/kernel/debug/tracing/trace_clock
    echo 16 > /sys/kernel/debug/tracing/buffer_size_kb
    echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_enter_getcpu/enable
    echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_exit_getcpu/enable


    echo 1 > /sys/kernel/debug/tracing/tracing_on
    $CMD
    echo 0 > /sys/kernel/debug/tracing/tracing_on
    head -n 3 /sys/kernel/debug/tracing/trace
}

ftrace_tracing()
{
    workload=$1
    CMD=$2

    echo nop > /sys/kernel/debug/tracing/current_tracer
    echo > /sys/kernel/debug/tracing/trace
    echo global > /sys/kernel/debug/tracing/trace_clock
    echo 16384 > /sys/kernel/debug/tracing/buffer_size_kb

    sudo trace-cmd record -e sys_enter_getcpu -e sys_exit_getcpu $CMD
    rm trace.dat*
}

perf_tracing()
{
    workload=$1
    CMD=$2

    sudo perf record -e 'syscalls:sys_enter_getcpu,syscalls:sys_exit_getcpu' -a $CMD > /dev/null
    sudo rm perf.data*
}

strace_tracing_fllight_recorder()
{
    workload=$1
    CMD=$2

    strace -egetcpu -q -t -f -o /dev/null $CMD
}

strace_tracing()
{
    workload=$1
    CMD=$2

    strace -egetcpu -q -t -f -o ./strace.txt $CMD
    sudo rm strace.txt
}

keep_cpu_busy_for_us=1
#events=2500
events=5000000
total_events=$((events * 2))
workload="getcpu_${keep_cpu_busy_for_us}_${total_events}"
cmd="./syscall-micro-benchmark ${keep_cpu_busy_for_us} ${events}"

repeat=30
#
#reset
#echo "$limiter None $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    $cmd
#done

#reset
#echo "$limiter Perf $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    perf_tracing "${workload}" "${cmd}"
#done

#reset
#echo "$limiter Ftrace flight recorder $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    ftrace_tracing_flight_recorder "${workload}" "${cmd}"
#done
#
#echo "$limiter Ftrace $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    ftrace_tracing "${workload}" "${cmd}"
#done
#echo nop > /sys/kernel/debug/tracing/current_tracer
#echo 0 > /sys/kernel/debug/tracing/events/syscalls/enable
#
#reset
#echo "$limiter Lttng flight recorder $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    lttng_tracing_flight_recorder "${workload}" "${cmd}"
#done
#
#echo "$limiter Lttng $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    lttng_tracing "${workload}" "${cmd}"
#done
#
#reset
#echo "$limiter Strace flight recorder $limiter" >> results.txt
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    strace_tracing_fllight_recorder "${workload}" "${cmd}"
#done

reset
echo "$limiter Strace $limiter" >> results.txt
for i in $(eval echo "{1..$repeat}")
do
    sleep 0.1
    strace_tracing "${workload}" "${cmd}"
done
