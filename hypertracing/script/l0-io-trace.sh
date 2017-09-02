#!/usr/bin/env bash
# set -x

#rm -rf ~/lttng-traces/bootup-tracing-*

#ssh root@ubuntu 'cat /dev/null > /sys/kernel/debug/tracing/trace'
# ssh ubuntu 'cd /home/abder/io_hypertracing && ./run.sh'


# number_writes=1000
# CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$number_writes oflag=sync iflag=sync"
# CMD="dd if=/dev/zero of=/tmp/test bs=1K count=$number_writes conv=fdatasync"

output="/home/abder/lttng-traces/simple-traces-benchmarks-01"
lttng create
# --snapshot
lttng enable-channel -k --subbuf-size=64K --num-subbuf=128 vm_channel
# lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall,kvm_x86_inj_virq,kvm_x86_apic_accept_irq,sched_switch,lttng_statedump*" -c vm_channel
#lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k "irq_softirq_raise,irq_softirq_entry,irq_softirq_exit,sched_*,sched_switch,lttng_statedump*" -c vm_channel
lttng enable-event -k "sched_wakeup,sched_switch" -c vm_channel
#lttng enable-event -k -a -c vm_channel

# lttng add-context -k -t pid -t tid -t procname
#lttng add-context --kernel --type=perf:cpu:cpu-cycles --type=perf:cpu:instructions

#ssh vm1 'lttng create block-io-traces;
#    lttng enable-channel -k --subbuf-size=4k --num-subbuf=32 vm_channel;
#    lttng enable-event -k \"block_getrq,block_rq*,block_bio_backmerge,block_bio_frontmerge,block_sleeprq\" -c vm_channel;'


lttng start
#./hypertime;$CMD;./hypertime end
#ssh vm1 "lttng start;$CMD;lttng stop;lttng destroy"
#ssh vm "./hypercall_benchmark" > /dev/null
#./sched-switch-micro-benchmark 1 3000 &
./sched-switch-micro-benchmark 2 1000
#sysbench --test=cpu --num-threads=2 --cpu-max-prime=5000 run
lttng stop
lttng view | wc -l

# lttng snapshot record --name=snapshot

#ssh vm1 "ps -eo pid,comm > process.txt"
lttng destroy

# /home/abder/utils/hypertracing/script/exits-cost.py $output
