lttng create
lttng enable-event -k -a
lttng add-context -k -t perf:cpu:context-switches
lttng add-context -k -t perf:cpu:page-fault

lttng enable-event -u -a
lttng add-context -u -t vpid -t vtid -t procname
lttng add-context -u -t perf:thread:page-fault
lttng add-context -u -t perf:thread:cache-misses 
lttng add-context -u -t perf:thread:context-switches
lttng add-context -u -t perf:thread:instructions 
lttng add-context -u -t perf:thread:cpu-cycles 

lttng start
LD_PRELOAD=liblttng-ust-cyg-profile.so ./main
lttng stop
lttng destroy
