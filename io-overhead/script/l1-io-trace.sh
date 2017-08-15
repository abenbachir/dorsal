#!/usr/bin/env bash

#CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$count oflag=sync iflag=sync"
#CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$count conv=fdatasync"

l1_no_tracing()
{
    count=$1
    CMD=$2
#    echo "count=$count, CMD=$CMD"
    lttng create hypertracing-l1-io_tracing-non-$count
    lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
    lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel
    lttng start
    ssh vm1 "./hypertime;$CMD;./hypertime end"
    lttng stop
    lttng view | wc
    lttng destroy
}

l1_lttng_tracing_enabled()
{
    count=$1
    CMD=$2
    lttng create hypertracing-l1-io_tracing-lttng-$count
    lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
    lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel

    ssh vm1 'lttng create block-io-traces;
        lttng enable-channel -k  vm_channel;
        lttng enable-event -k "sched_switch,block_getrq,block_rq*,block_bio_backmerge,block_bio_frontmerge,block_sleeprq" -c vm_channel;
        lttng add-context -k -t pid -t tid -t procname'

    lttng start
    ssh vm1 "lttng start;$CMD;lttng stop;lttng view | wc -l;echo \"collected events\";lttng destroy"

    lttng stop
    lttng view | wc
    lttng destroy
}

l1_perf_tracing_enabled()
{
    count=$1
    CMD=$2
    lttng create hypertracing-l1-io_tracing-perf-$count
    lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
    lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel
    lttng start

    ssh vm1 "sudo perf record -e 'block:block_getrq,block:block_rq*,block:block_bio_backmerge,block:block_bio_frontmerge,block:block_sleeprq' -a $CMD > /dev/null"
    ssh vm1 "sudo pkill perf; sudo rm perf.data"

    lttng stop
    lttng view | wc
    lttng destroy
}


for number in 1000
do
    for i in {1..1}
        do
        count=${number}
        CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$count oflag=sync iflag=sync"

        l1_lttng_tracing_enabled "${count}" "${CMD}"
        sleep 2

#        l1_no_tracing "${count}" "${CMD}"
#        sleep 2
#
#        l1_perf_tracing_enabled "${count}" "${CMD}"
#        sleep 2

    done
    echo ""
done