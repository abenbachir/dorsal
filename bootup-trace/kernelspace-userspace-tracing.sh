#!/usr/bin/env bash
set -x

lttng create kernelspace-tracing
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel
lttng enable-event -k "sched_*,kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k -a -c vm_channel
lttng start

ssh root@ubuntu 'sudo insmod /home/abder/fgraph/fgraph.ko;
/home/abder/simple-program-ins-dohypercall
sudo rmmod fgraph;'

lttng stop
lttng destroy

ssh root@ubuntu 'cat /proc/kallsyms > /home/abder/symbols.txt'
ssh ubuntu 'nm -an simple-program-ins-dohypercall > program-symbols.txt'
scp ubuntu:~/symbols.txt .
scp ubuntu:~/program-symbols.txt .

