#!/usr/bin/env bash

linuxsource="linux"
target="ubuntu2"
# virsh setvcpus --live ubuntu 4



#scp ~/$linuxsource/kernel/trace/trace_sched_switch.c $target:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/trace/trace_functions_graph.c $target:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/hypercall.c $target:~/linux/kernel/

scp ~/$linuxsource/kernel/trace/Makefile $target:~/linux/kernel/trace/
scp ~/$linuxsource/kernel/trace/trace.c $target:~/linux/kernel/trace/
scp ~/$linuxsource/kernel/trace/trace.h $target:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/trace/trace_functions.c $target:~/linux/kernel/trace/
scp ~/$linuxsource/kernel/trace/trace_hypergraph.c $target:~/linux/kernel/trace/
scp ~/$linuxsource/kernel/trace/trace_hyperbootlevel.c $target:~/linux/kernel/trace/

# scp ~/$linuxsource/init/main.c $target:~/linux/init/
# scp ~/$linuxsource/init/Makefile $target:~/linux/init/



ssh $target 'cd linux; make -j$(nproc) && sudo make modules_install && sudo make install;'

#ssh $target 'sudo shutdown now'
#ssh $target 'sudo reboot'