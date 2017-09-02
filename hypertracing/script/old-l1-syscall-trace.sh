#!/usr/bin/env bash
# set -x

output="/home/abder/lttng-traces/syscall-traces-0-1"
lttng create simple-hypercall --output=$output
lttng enable-channel -k --subbuf-size=1024k --num-subbuf=128 vm_channel
lttng enable-event -k "kvm_x86_exit,kvm_x86_entry,kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k --syscall getcpu -c vm_channel
#lttng add-context -k -t pid -t tid -t procname

#ssh vm1 'lttng create block-io-traces;
#    lttng enable-channel -k --subbuf-size=4k --num-subbuf=32 vm_channel;
#    lttng enable-event -k \"block_getrq,block_rq*,block_bio_backmerge,block_bio_frontmerge,block_sleeprq\" -c vm_channel;'


lttng start
#./hypertime;$CMD;./hypertime end
#ssh vm1 "lttng start;$CMD;lttng stop;lttng destroy"

ssh vm "./syscall-micro-benchmark"

lttng stop
#ssh vm1 "ps -eo pid,comm > process.txt"
lttng view | wc -l
lttng destroy

/home/abder/utils/hypertracing/script/exits-cost.py $output
