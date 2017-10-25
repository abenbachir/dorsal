lttng create
lttng enable-event -u "lttng_ust_cyg*"
lttng add-context -u -t vpid -t vtid -t procname
lttng start
LD_PRELOAD=liblttng-ust-cyg-profile.so ./mergesort >> tracing-data.csv
LD_PRELOAD=liblttng-ust-cyg-profile.so ./mergesort >> tracing-data.csv
LD_PRELOAD=liblttng-ust-cyg-profile.so ./mergesort >> tracing-data.csv
LD_PRELOAD=liblttng-ust-cyg-profile.so ./mergesort >> tracing-data.csv
LD_PRELOAD=liblttng-ust-cyg-profile.so ./mergesort >> tracing-data.csv
lttng stop
lttng destroy
