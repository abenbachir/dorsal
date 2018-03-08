

scp guest-trace.sh abder@ubuntu:/home/abder

virsh vcpupin ubuntu 0 7
virsh vcpuinfo ubuntu
output="/home/abder/lttng-traces/host-trace"

rm -rf $output
lttng create guest --output="$output"
lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
lttng enable-event -k "sched_*" -c vm_channel
lttng enable-event -k "vmsync*" -c vm_channel
# lttng enable-event -k "timer_*" -c vm_channel
# lttng enable-event -k "lttng_statedump*" -c vm_channel
# lttng enable-event -k "irq_*" -c vm_channel
lttng enable-event -k "kvm_x86_exit,kvm_x86_entry" -c vm_channel
lttng enable-event -k --syscall -a -c vm_channel
lttng add-context -k -t pid -t tid -t procname
lttng start

ssh abder@ubuntu '/home/abder/guest-trace.sh' &
sleep 0.5
virsh suspend ubuntu
# sleep 1
virsh vcpupin ubuntu 0 5
virsh resume ubuntu
sleep 2
lttng stop
lttng destroy

rm -rf /home/abder/lttng-traces/guest-trace
scp -r abder@ubuntu:/home/abder/lttng-traces/guest-trace /home/abder/lttng-traces