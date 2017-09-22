#!/usr/bin/env bash
set -x


lttng create guest
 lttng enable-channel -k --subbuf-size=128K --num-subbuf=128 chann
# lttng enable-channel -k --subbuf-size=16K --num-subbuf=128 --session=guest chan


lttng enable-event -k "kvm_x86_hypercall" -c chann

virsh start ubuntu2
virsh vcpupin ubuntu2 0 0
virsh vcpupin ubuntu2 1 1
virsh vcpuinfo ubuntu2

lttng start


sleep 5;
#sleep 20;

#lttng stop guest
#
#lttng stop host
#
lttng destroy

#./dump-symbols.sh

#babm
