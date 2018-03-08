

# 	-serial stdio -hda $qcow2 \


#ssh root@VM 'cd /sys/kernel/debug/tracing/;
#echo 0 > tracing_on;
#echo hypertrace > current_tracer;
#echo 1 > tracing_on'

lttng create shutdown
lttng enable-channel -k --subbuf-size=128K --num-subbuf=256 vm_channel
# lttng enable-event -k "kvm_x86_entry,kvm_x86_exit,kvm_x86_hypercall" -c vm_channel
lttng enable-event -k "kvm_x86_hypercall" -c vm_channel
lttng add-context -k -t pid -t tid -t procname -c vm_channel
lttng start 


#ssh abder@VM 'sudo shutdown now' &


sleep 10

lttng stop
lttng view | wc -l
lttng destroy
