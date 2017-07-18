
# run without tracing 
python dd.py 30

# run with tracing
for i in {1..30}
do
	lttng create dd-tracing
	# lttng enable-channel -k --subbuf-size=16777216 --num-subbuf=128 vm_channel
	# lttng enable-event -k -a -c vm_channel
	lttng enable-event -k "sched_switch" -c vm_channel
	# lttng enable-event -k --syscall -a -c vm_channel
	lttng enable-event -k --syscall open,close,read,write -c vm_channel
	# lttng enable-event -k "ext4_da_write_begin,ext4_da_write_end" -c vm_channel
	lttng start

	python dd.py 1 1

	lttng stop
	lttng destroy
done

