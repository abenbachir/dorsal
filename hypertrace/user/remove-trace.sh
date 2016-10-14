


lttng create vm_bootup
lttng enable-channel -k --subbuf-size=2097152 --num-subbuf=32 vm_channel
lttng enable-event -k -a -c vm_channel
#lttng enable-event -k  "sched_*,kvm_*" -c vm_channel
lttng enable-event -u 'qemu:guest_hypertrace' -c vm_channel

lttng start

ssh root@ubuntu '/home/abder/my-hypertrace-softmmu-benchmark' > /home/abder/utils/hypercall/hypertrace-kvm-enabled.dat

lttng stop
#lttng view > trace.log
lttng destroy


