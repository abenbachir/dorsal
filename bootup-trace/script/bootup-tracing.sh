#!/usr/bin/env bash
set -x

#rm -rf ~/lttng-traces/bootup-tracing-*

#ssh root@ubuntu 'cat /dev/null > /sys/kernel/debug/tracing/trace'

output=/home/abder/lttng-traces/bootup

rm -rf $output
lttng create host --output=$output/host
lttng create guest --output=$output/guest

lttng enable-channel -k --session=host --subbuf-size=128K --num-subbuf=128 h_chan
lttng enable-channel -k --session=guest --subbuf-size=128K --num-subbuf=128 g_chan

lttng enable-event -k "sched*" -c h_chan -s host
lttng enable-event -k "kvm*,kvm_x86_hypercall" -c g_chan -s guest

# virsh start ubuntu2
# virsh vcpupin ubuntu2 0 0
# virsh vcpupin ubuntu2 1 1
# virsh vcpuinfo ubuntu2

lttng start host
lttng start guest


sleep 3 # passe through bootloader


lttng stop host
lttng stop guest

lttng destroy --all

#./dump-symbols.sh

#babm
