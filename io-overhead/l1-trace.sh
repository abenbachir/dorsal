#!/usr/bin/env bash

number_writes=10000
CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$number_writes oflag=sync iflag=sync"

l1_tracing_disbaled()
{
    lttng create io-hypertracing-l1-tracing-disabled-$number_writes
    lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
    lttng enable-event -k "kvm_*" -c vm_channel
    lttng start
    ssh vm1 "$CMD"
    lttng stop
    lttng view | wc
    lttng destroy
}

l1_tracing_enabled()
{
    lttng create io-hypertracing-l1-tracing-enabled-$number_writes
    lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
    lttng enable-event -k "kvm_*" -c vm_channel

    ssh vm1 'lttng create block-io-traces;
        lttng enable-channel -k --subbuf-size=4k --num-subbuf=32 vm_channel;
        lttng enable-event -k \"block_getrq,block_rq*,block_bio_backmerge,block_bio_frontmerge,block_sleeprq\" -c vm_channel;'

    lttng start

    ssh vm1 "lttng start;$CMD;lttng stop;lttng destroy"

    lttng stop
    lttng view | wc
    lttng destroy
}

l1_tracing_disbaled
sleep 2
l1_tracing_enabled