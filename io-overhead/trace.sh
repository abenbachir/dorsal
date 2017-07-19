#!/usr/bin/env bash
set -x

#rm -rf ~/lttng-traces/bootup-tracing-*

#ssh root@ubuntu 'cat /dev/null > /sys/kernel/debug/tracing/trace'

lttng create io-hypertracing-tracing
lttng enable-channel -k --subbuf-size=1MB --num-subbuf=128 vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
lttng start

ssh ubuntu 'cd /home/abder/io_hypertracing && ./run.sh'

lttng stop
lttng destroy