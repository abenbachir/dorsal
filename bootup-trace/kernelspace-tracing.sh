#!/usr/bin/env bash
set -x

lttng create kernelspace-tracing
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel
lttng enable-event -k "kvm_x86_entry,kvm_x86_exit,kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k -a -c vm_channel
lttng start
ssh ubuntu 'sudo insmod ~/fgraph/fgraph.ko; ./simple-program-ins-dohypercall; sudo rmmod fgraph;'
#ssh root@ubuntu '/home/abder/simple-program-ins-dohypercall'
lttng stop
lttng destroy

ssh ubuntu "nm -an simple-program-ins-dohypercall > program-symbols.txt"
ssh ubuntu "sudo cat /proc/kallsyms > symbols.txt"
scp ubuntu:~/symbols.txt .
scp ubuntu:~/program-symbols.txt .
