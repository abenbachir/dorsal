#!/usr/bin/env bash

#virsh vcpupin VM1 0 7
#virsh vcpupin VM1 1 6
target_l1=vm1
target_l2=nested-vm
trace_dir="/home/abder/lttng-traces/tracers/syscall"
drop_cache='free && sync && echo 1 > /proc/sys/vm/drop_caches && sync && echo 2 > /proc/sys/vm/drop_caches && sync && echo 3 > /proc/sys/vm/drop_caches && free'
swapoff='swapoff -a && swapon -a'
limiter="======================================================"

reset_ftrace()
{
    ssh root@$target_l1 "ssh $target_l2 'echo nop > /sys/kernel/debug/tracing/current_tracer;echo 0 > /sys/kernel/debug/tracing/events/enable'"
}
reset(){
    ssh $target_l1 "ssh $target_l2 'sudo pkill lttng; pgrep lttng -l'"
    reset_ftrace
    ssh root@$target_l1 "ssh $target_l2 '$drop_cache'"
}

start_host_tracing_snapshot() {
    output=$1
    lttng create host-traces --output="$output" --snapshot
    lttng enable-channel -k --subbuf-size=8K --num-subbuf=2 vm_channel
    lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
    lttng start
}
stop_host_tracing_snapshot() {
    lttng stop
    lttng snapshot record
    lttng destroy
}
start_host_tracing() {
    output=$1
    lttng create host-traces --output="$output"
    lttng enable-channel -k --subbuf-size=8K --num-subbuf=2 vm_channel
    lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
    lttng start
}
stop_host_tracing() {
    lttng stop
    lttng view | wc -l
    lttng destroy
}

no_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/none/l2-syscall_benchmark-none-${workload}-$(dbus-uuidgen)"
    start_host_tracing "${output}"

    ssh $target_l1 "ssh $target_l2 '$CMD'"

    stop_host_tracing
}

hypertracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/hypertracing/l2-syscall_benchmark-hyperT-${workload}-$(dbus-uuidgen)"

    ssh $target_l1 "ssh $target_l2 'sudo insmod hypertracing/syscall_hypertracing_guest.ko'"

    start_host_tracing_snapshot "${output}"

    ssh $target_l1 "ssh $target_l2 '$CMD'"

    stop_host_tracing_snapshot
    ssh $target_l1 "ssh $target_l2 'sudo rmmod syscall_hypertracing_guest'"
}

hypertracing_compress()
{
    workload=$1
    CMD=$2
    output="$trace_dir/hypertracing/l2-syscall_benchmark-hyperT_compress_3-${workload}-$(dbus-uuidgen)"

    ssh $target_l1 "ssh $target_l2 'sudo insmod hypertracing/syscall_hypertracing_compress_guest.ko'"

    start_host_tracing_snapshot "${output}"

    ssh $target_l1 "ssh $target_l2 '$CMD'"

    stop_host_tracing_snapshot
    ssh $target_l1 "ssh $target_l2 'sudo rmmod syscall_hypertracing_compress_guest'"
}

lttng_tracing_flight_recorder()
{
    workload=$1
    CMD=$2
    output="$trace_dir/lttng/l2-syscall_benchmark-lttng_flight_recorder-${workload}-$(dbus-uuidgen)"

    ssh $target_l1 "ssh $target_l2 'rm -rf lttng-traces/*;
        lttng create syscall-traces --snapshot;
        lttng enable-channel -k --subbuf-size=8K --num-subbuf=2 vm_channel;
        lttng enable-event -k --syscall getcpu -c vm_channel'"

    start_host_tracing "${output}"

    ssh $target_l1 "ssh $target_l2 'lttng start && $CMD && lttng stop; lttng destroy'"

    stop_host_tracing
}

lttng_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/lttng/l2-syscall_benchmark-lttng-${workload}-$(dbus-uuidgen)"

    ssh $target_l1 "ssh $target_l2 'rm -rf lttng-traces/*;
        lttng create syscall-traces;
        lttng enable-channel -k --subbuf-size=128K --num-subbuf=128 vm_channel;
        lttng enable-event -k --syscall getcpu -c vm_channel'"

    start_host_tracing "${output}"

    ssh $target_l1 "ssh $target_l2 'lttng start && $CMD && lttng stop; lttng view | wc -l;echo \"collected events\";lttng destroy'"

    stop_host_tracing
}


ftrace_tracing_flight_recorder()
{
    workload=$1
    CMD=$2
    output="$trace_dir/ftrace/l2-syscall_benchmark-ftrace_flight_recorder-${workload}-$(dbus-uuidgen)"

    ssh root@$target_l1 "ssh $target_l2 'echo nop > /sys/kernel/debug/tracing/current_tracer;
        echo > /sys/kernel/debug/tracing/trace;
        echo global > /sys/kernel/debug/tracing/trace_clock;
        echo 16384 > /sys/kernel/debug/tracing/buffer_size_kb;
        echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_enter_getcpu/enable;
        echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_exit_getcpu/enable'"

    start_host_tracing "${output}"

    ssh root@$target_l1 "ssh $target_l2 'echo 1 > /sys/kernel/debug/tracing/tracing_on &&
    $CMD && echo 0 > /sys/kernel/debug/tracing/tracing_on;
    head -n 3 /sys/kernel/debug/tracing/trace'"

    stop_host_tracing
}

ftrace_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/ftrace/l2-syscall_benchmark-ftrace-${workload}-$(dbus-uuidgen)"

    ssh root@$target_l1 "ssh $target_l2 'echo nop > /sys/kernel/debug/tracing/current_tracer;
        echo > /sys/kernel/debug/tracing/trace;
        echo global > /sys/kernel/debug/tracing/trace_clock;
        echo 16384 > /sys/kernel/debug/tracing/buffer_size_kb'"

    start_host_tracing "${output}"
    ssh root@$target_l1 "ssh $target_l2 'sudo trace-cmd record -e sys_enter_getcpu -e sys_exit_getcpu $CMD'"

#    ssh root@$target_l1 "ssh $target_l2 'echo 1 > /sys/kernel/debug/tracing/tracing_on &&
#    $CMD && echo 0 > /sys/kernel/debug/tracing/tracing_on;
#    head -n 3 /sys/kernel/debug/tracing/trace'"

    stop_host_tracing
    ssh root@$target_l1 "ssh $target_l2 'head -n 4 /sys/kernel/debug/tracing/trace; rm results.txt; rm trace.dat*'"
}

perf_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/perf/l2-syscall_benchmark-perf-${workload}-$(dbus-uuidgen)"

    start_host_tracing "${output}"

    ssh $target_l1 "ssh $target_l2 'sudo perf record -e 'syscalls:sys_enter_getcpu,syscalls:sys_exit_getcpu' -a $CMD > /dev/null'"

    stop_host_tracing
    ssh $target_l1 "ssh $target_l2 'sudo pkill perf; sudo rm perf.data*'"
}

strace_tracing_fllight_recorder()
{
    workload=$1
    CMD=$2
    output="$trace_dir/strace/l2-syscall_benchmark-strace_flight_recorder-${workload}-$(dbus-uuidgen)"

    start_host_tracing "${output}"

    ssh $target_l1 "ssh $target_l2 'strace -egetcpu -q -t -f -o /dev/null $CMD'"

    stop_host_tracing
}

strace_tracing()
{
    workload=$1
    CMD=$2
    output="$trace_dir/strace/l2-syscall_benchmark-strace-${workload}-$(dbus-uuidgen)"

    start_host_tracing "${output}"

    ssh $target_l1 "ssh $target_l2 'strace -egetcpu -q -t -f -o ./strace.txt $CMD'"

    stop_host_tracing
    ssh $target_l1 "ssh $target_l2 'sudo rm strace.txt'"
}

keep_cpu_busy_for_us=1
#events=2500
events=5000000
total_events=$((events * 2))
workload="getcpu_${keep_cpu_busy_for_us}_${total_events}"
cmd="./syscall-micro-benchmark ${keep_cpu_busy_for_us} ${events}"

repeat=30

#reset
#echo "$limiter None $limiter"
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    no_tracing "${workload}" "${cmd}"
#done

reset
echo "$limiter Perf $limiter"
for i in $(eval echo "{1..$repeat}")
do
    sleep 0.1
    perf_tracing "${workload}" "${cmd}"
done

#reset
#echo "$limiter Hypertracing $limiter"
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    hypertracing "${workload}" "${cmd}"
#    sleep 0.1
#    hypertracing_compress "${workload}" "${cmd}"
#done


#reset
#echo "$limiter Strace $limiter"
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    strace_tracing_fllight_recorder "${workload}" "${cmd}"
#    sleep 0.1
#    strace_tracing "${workload}" "${cmd}"
#done

#reset;
#echo "$limiter Ftrace $limiter"
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    ftrace_tracing_flight_recorder "${workload}" "${cmd}"
#    sleep 0.1
#    ftrace_tracing "${workload}" "${cmd}"
#done
#reset_ftrace
#
#reset
#echo "$limiter Lttng $limiter"
#ssh $target_l1 "ssh $target_l2 'sudo lttng-sessiond -d; pgrep lttng -l'"
#for i in $(eval echo "{1..$repeat}")
#do
#    sleep 0.1
#    lttng_tracing_flight_recorder "${workload}" "${cmd}"
#    sleep 0.1
#    lttng_tracing "${workload}" "${cmd}"
#done
#ssh $target_l1 "ssh $target_l2 'sudo pkill lttng; pgrep lttng -l'"

