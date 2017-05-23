set -x

lttng create hypercall-benchmark
lttng enable-channel -k --subbuf-size=16777216 --num-subbuf=64 vm_channel
#lttng enable-event -k -a --channel vm_channel
#lttng enable-event -k  "abder_*" -c vm_channel
#lttng enable-event -u -a --channel vm_channel
lttng enable-event -k "kvm_x86_exit" --filter="exit_reason == 18" -c vm_channel
lttng enable-event -k "kvm_x86_hypercall,kvm_x86_entry" -c vm_channel

lttng start

#ssh abder@ubuntu '/home/abder/hypercall_benchmark' > ./hypercall-with-trace-enabled.dat

#lttng stop
#lttng destroy

