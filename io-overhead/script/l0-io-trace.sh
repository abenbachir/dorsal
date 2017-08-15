#!/usr/bin/env bash
# set -x

#rm -rf ~/lttng-traces/bootup-tracing-*

#ssh root@ubuntu 'cat /dev/null > /sys/kernel/debug/tracing/trace'
# ssh ubuntu 'cd /home/abder/io_hypertracing && ./run.sh'


number_writes=1000
CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$number_writes oflag=sync iflag=sync"
# CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$number_writes conv=fdatasync"


lttng create io-hypertracing-l1-tracing-enabled-$number_writes-async
lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_inj_virq,kvm_x86_apic_accept_irq,kvm_x86_hypercall,sched_switch,lttng_statedump*" -c vm_channel
lttng add-context -k -t pid -t tid -t procname

#ssh vm1 'lttng create block-io-traces;
#    lttng enable-channel -k --subbuf-size=4k --num-subbuf=32 vm_channel;
#    lttng enable-event -k \"block_getrq,block_rq*,block_bio_backmerge,block_bio_frontmerge,block_sleeprq\" -c vm_channel;'

sudo
lttng start
#./hypertime;$CMD;./hypertime end
#ssh vm1 "lttng start;$CMD;lttng stop;lttng destroy"

lttng stop
ssh vm1 "ps -eo pid,comm > process.txt"
lttng view | wc
lttng destroy
