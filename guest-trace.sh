

#sudo insmod ptp.ko
#sudo insmod ptp_kvm.ko
#/home/abder/lttng/lttng-modules/control-addons.sh load

output="/home/abder/lttng-traces/guest-trace"

rm -rf $output
lttng create guest --output="$output"
lttng enable-channel -k --subbuf-size=256K --num-subbuf=64 vm_channel
lttng enable-event -k "sched_*" -c vm_channel
lttng enable-event -k "vmsync*" -c vm_channel
lttng enable-event -k "timer_*" -c vm_channel
lttng enable-event -k "lttng_statedump*" -c vm_channel
lttng enable-event -k "irq_*" -c vm_channel
lttng enable-event -k --syscall -a -c vm_channel
lttng start

sysbench cpu --threads=1 --cpu-max-prime=5000 --time=1 run
# sysbench fileio --file-total-size=100MB --file-test-mode=rndrw --time=3 --max-requests=0 run

lttng stop
lttng destroy