#!/usr/bin/env bash

linuxsource="linux-dirty"
target="vm"
# virsh setvcpus --live ubuntu 4



#scp ~/$linuxsource/kernel/trace/trace_sched_switch.c $target:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/trace/trace_functions_graph.c $target:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/hypercall.c $target:~/linux/kernel/

#scp ~/$linuxsource/kernel/trace/Makefile $target:~/linux/kernel/trace/
# scp ~/$linuxsource/kernel/trace/trace.c $target:~/linux/kernel/trace/
# scp ~/$linuxsource/kernel/trace/trace.h $target:~/linux/kernel/trace/

#scp ~/$linuxsource/kernel/trace/trace_hypergraph.c $target:~/linux/kernel/trace/
# scp ~/$linuxsource/kernel/trace/trace_hyperbootlevel.c $target:~/linux/kernel/trace/
# scp ~/$linuxsource/kernel/trace/trace_hypertrace.c $target:~/linux/kernel/trace/

# scp ~/$linuxsource/init/main.c $target:~/linux/init/
# scp ~/$linuxsource/init/Makefile $target:~/linux/init/


scp ~/$linuxsource/arch/x86/kernel/ftrace_64.S $target:~/linux/arch/x86/kernel/

ssh $target 'cd linux; make -j$(nproc) && sudo make modules_install && sudo make install;'

#ssh $target 'sudo shutdown now'
#ssh $target 'sudo reboot'
