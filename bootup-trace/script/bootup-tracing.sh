#!/usr/bin/env bash
set -x

#rm -rf ~/lttng-traces/bootup-tracing-*

#ssh root@ubuntu 'cat /dev/null > /sys/kernel/debug/tracing/trace'

output=/home/abder/lttng-traces/bootup

rm -rf $output
lttng create host --output=$output/host
lttng create guest --output=$output/guest
# lttng enable-channel -k --subbuf-size=128 --num-subbuf=128 --session=host chann
# lttng enable-channel -k --subbuf-size=16 --num-subbuf=128 --session=guest chan

lttng enable-event -k "sched*" -c chann -s host
lttng enable-event -k "kvm*,kvm_x86_hypercall" -c chann -s guest

# virsh start ubuntu2
# virsh vcpupin ubuntu2 0 0
# virsh vcpupin ubuntu2 1 1
# virsh vcpuinfo ubuntu2

lttng start host

lttng start guest


sleep 3 # passe through bootloader

#sleep 15;
#sleep 20;

lttng stop guest

lttng stop host

lttng destroy --all

#./dump-symbols.sh

#babm
