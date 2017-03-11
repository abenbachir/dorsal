lttng create
lttng enable-event -k -a
lttng enable-event -u "lttng_ust_cyg*"
lttng start
LD_PRELOAD=liblttng-ust-cyg-profile.so ./main
lttng stop
lttng destroy
