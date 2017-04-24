lttng create
lttng enable-event -u "lttng_ust_cyg*"
lttng start
LD_PRELOAD=liblttng-ust-cyg-profile.so ./mergesort
lttng stop
lttng destroy
