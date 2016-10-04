set -x

lttng create hypercall_trace
lttng enable-channel --kernel --num-subbuf 16 --subbuf-size 512k vm_channel
lttng enable-event -k -a --channel vm_channel
#lttng enable-event -k  "sched_*,kvm_*" -c vm_channel
lttng enable-event -u -a --channel vm_channel
#lttng enable-event -u "qemu:guest*" -c vm_channel
lttng start

ssh abder@ubuntu '/home/abder/hypercall_sampler'

lttng stop
lttng view > traces.log
lttng destroy

