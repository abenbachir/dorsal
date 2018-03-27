

scp guest-trace.sh abder@ubuntu:/home/abder

virsh vcpupin ubuntu 0 5
# virsh vcpupin ubuntu 1 6
# filters="$ctx.cpu_id == 5 || $ctx.cpu_id == 6"
filters="$ctx.cpu_id == 5"
virsh vcpuinfo ubuntu
output="/home/abder/lttng-traces/host-trace"


# rm -rf /home/abder/lttng-traces/guest-trace
# scp -r abder@ubuntu:/home/abder/lttng-traces/guest-trace /home/abder/lttng-traces


hypercall_start()
{
	echo "hypercall"
	rm -rf $output
	lttng create guest --output="$output"
	lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
	lttng enable-event -k "sched_switch" --filter "$filters" -c vm_channel
	lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
	# lttng enable-event -k --syscall -a -c vm_channel
	# lttng add-context -k -t pid -t tid -t procname
	lttng start

	ssh abder@ubuntu "/home/abder/guest-trace.sh hypercall $1"

	lttng stop
	lttng destroy
}

hypercall_batching_start()
{
	echo "hypercall_batching"
	rm -rf $output
	lttng create guest --output="$output"
	lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
	lttng enable-event -k "sched_switch" --filter "$filters" -c vm_channel
	lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
	# lttng enable-event -k --syscall -a -c vm_channel
	# lttng add-context -k -t pid -t tid -t procname
	lttng start

	ssh abder@ubuntu "/home/abder/guest-trace.sh hypercall_batching $1"

	lttng stop
	lttng destroy
}
shared_memory_start()
{
	echo "shared_memory"
	rm -rf $output
	lttng create guest --output="$output"
	lttng enable-channel -k --subbuf-size=1M --num-subbuf=128 vm_channel
	lttng enable-event -k "sched_switch" --filter "$filters" -c vm_channel
	lttng enable-event -k "kvm_x86_exit,kvm_x86_entry" -c vm_channel
	# lttng enable-event -k --syscall -a -c vm_channel
	# lttng add-context -k -t pid -t tid -t procname
	lttng start

	ssh abder@ubuntu "/home/abder/guest-trace.sh memory $1"

	lttng stop
	lttng destroy
}

multi_level_start()
{
	echo "multi_level"
	/home/abder/lttng/lttng-addons-tahini/control-addons.sh load
	lttng list -k | grep vmsync
	rm -rf $output
	lttng create guest --output="$output"
	lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
	lttng enable-event -k "sched_switch" --filter "$filters" -c vm_channel
	lttng enable-event -k "vmsync*" -c vm_channel
	# lttng enable-event -k "timer_*" -c vm_channel
	# lttng enable-event -k "lttng_statedump*" -c vm_channel
	# lttng enable-event -k "irq_*" -c vm_channel
	lttng enable-event -k "kvm_x86_exit,kvm_x86_hypercall,kvm_x86_entry" -c vm_channel
	# lttng enable-event -k --syscall -a -c vm_channel
	# lttng add-context -k -t pid -t tid -t procname
	lttng start

	ssh abder@ubuntu "/home/abder/guest-trace.sh multilevel $1"

	lttng stop
	lttng destroy
	/home/abder/lttng/lttng-addons-tahini/control-addons.sh unload
}
lttng_init()
{
	sudo lttng-sessiond -d
}
lttng_kill()
{
	sudo pkill lttng
}
# lttng_kill
# lttng_init


# hypercall_start "cpu"
# hypercall_batching_start "cpu"
# multi_level_start "cpu"
# shared_memory_start "cpu"
# 38690

# hypercall_start "mem"
# hypercall_batching_start "mem"

# shared_memory_start "mem"
# hypercall_start "io"



shared_memory_start "io"
multi_level_start "io"
hypercall_start "io"
hypercall_batching_start "io"