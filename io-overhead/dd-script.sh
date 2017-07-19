
# run without tracing 
python dd.py 60

# run with tracing
for i in {1..60}
do
	lttng create io-hypertracing-tracing
	lttng enable-channel -k --subbuf-size=4k --num-subbuf=32 vm_channel
	lttng enable-event -k "block_getrq,block_rq*" -c vm_channel
	lttng enable-event -k "block_bio_backmerge,block_bio_frontmerge" -c vm_channel
	lttng enable-event -k "block_sleeprq" -c vm_channel
	lttng start

	python dd.py 1 1

	lttng stop
	lttng destroy
done

