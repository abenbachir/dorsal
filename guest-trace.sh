#!/usr/bin/env bash
sudo service chrony stop
sudo rmmod ptp_kvm
sudo rmmod ptp

if [ $# -lt 1 ]
then
        echo "Usage : $0 [baseline|hypercall|memory|multilevel]"
        exit
fi
if [ $# -lt 2 ]
then
        echo "Usage : $1 [cpu|mem|io]"
        exit
fi

#sudo insmod ptp.ko
#sudo insmod ptp_kvm.ko
#/home/abder/lttng/lttng-modules/control-addons.sh load

output="/home/abder/lttng-traces/guest-trace"

lttng_init()
{
	sudo lttng-sessiond -d
}
lttng_kill()
{
	sudo pkill lttng
}
workload()
{
	workload_type=$1
	for index in {1..3}
	do
		case "$workload_type" in
		cpu)
			sysbench --test=mutex --mutex-num=1 --mutex-locks=50000000 --mutex-loops=1 run | grep "avg:"
			;;
		mem)
			sysbench --test=memory --memory-block-size=1K --memory-total-size=5G run | grep "execution time"
		    ;;
		io)
			size="1G"
			sysbench --test=fileio --file-total-size=$size --verbosity=0 prepare
			sysbench --test=fileio --file-total-size=$size --file-test-mode=rndwr --max-time=30 --max-requests=0 run | grep "execution time"
		    sysbench --test=fileio --file-total-size=$size --verbosity=0 cleanup
		    ;;
		*) echo "unkown workload $workload_type"
		   ;;
		esac
	done
}
hypercall_start()
{
	echo "hypercall"
	lttng_kill
	sudo insmod /home/abder/vm_friendly/hypermod.ko
	echo 1 > /proc/hypermod 
	
	workload $1

	echo 0 > /proc/hypermod
	sudo rmmod hypermod
	lttng_init
}
hypercall_batching_start()
{
	echo "hypercall_batching_start"
	lttng_kill
	sudo insmod /home/abder/vm_friendly/hypermod_batching.ko
	echo 1 > /proc/hypermod 
	
	workload $1

	echo 0 > /proc/hypermod
	sudo rmmod hypermod_batching
	lttng_init
}
shared_memory_start()
{
	echo "shared_memory"
	rm -rf $output
	lttng create guest --snapshot --output="$output"
	lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
	lttng enable-event -k "sched_switch" -c vm_channel
	lttng enable-event -k --syscall -a -c vm_channel
	lttng start

	workload $1

	lttng stop
	lttng destroy
}
multi_level_start()
{
	echo "multi_level"
	/home/abder/lttng/lttng-modules/control-addons.sh load
	# lttng list -k | grep vmsync
	rm -rf $output
	lttng create guest --output="$output"
	lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
	lttng enable-event -k "sched_switch" -c vm_channel
	lttng enable-event -k "vmsync*" -c vm_channel
	lttng enable-event -k --syscall -a -c vm_channel
	lttng start

	workload $1

	lttng stop
	lttng destroy
	/home/abder/lttng/lttng-modules/control-addons.sh unload
}


# lttng_kill
# lttng_init

case "$1" in
baseline)
	lttng_kill

	workload $2

	lttng_init
	;;
hypercall)
	hypercall_start $2 
    ;;
hypercall_batching)
	hypercall_batching_start $2 
    ;;
memory)
	shared_memory_start $2
    ;;
multilevel)
	multi_level_start $2
    ;;
*) echo "unkown command $1"
   ;;
esac