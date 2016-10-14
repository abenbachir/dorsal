set -x

lttng create hypercall_trace
lttng enable-channel --kernel --num-subbuf 16 --subbuf-size 512k vm_channel
lttng enable-event -k -a --channel vm_channel
#lttng enable-event -k  "abder_*" -c vm_channel
#lttng enable-event -u -a --channel vm_channel

lttng start

ssh abder@ubuntu '/home/abder/hypercall_benchmark' > ./hypercall-with-trace-enabled.dat

lttng stop
lttng destroy

