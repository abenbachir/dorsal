#!/usr/bin/env bash
set -x

#rm -rf ~/lttng-traces/bootup-tracing-*

#ssh root@ubuntu 'cat /dev/null > /sys/kernel/debug/tracing/trace'

lttng create nested-l3-bootup-tracing
lttng enable-channel -k --subbuf-size=16777216 --num-subbuf=128 vm_channel
# lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
#lttng enable-event -k "hypergraph_host" -c vm_channel
#lttng enable-event -k -a -c vm_channel
lttng start

ssh abder@vm1 'ssh abder@nested-vm2 "sudo virsh start nested-nested-vm3" '

#sleep 1 # passe through bootloader

#sleep 15;
#sleep 20;

#lttng stop
#lttng view
#lttng destroy

#./dump-symbols.sh

#babm