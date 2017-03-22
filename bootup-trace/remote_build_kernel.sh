#!/usr/bin/env bash

linuxsource="linux"
virsh setvcpus --live ubuntu 4

#scp ~/$linuxsource/kernel/trace/trace_functions.c ubuntu:~/linux/kernel/trace/
scp ~/$linuxsource/kernel/trace/trace_hypergraph.c ubuntu:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/trace/trace_sched_switch.c ubuntu:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/trace/trace_functions_graph.c ubuntu:~/linux/kernel/trace/
#scp ~/$linuxsource/kernel/hypercall.c ubuntu:~/linux/kernel/
#scp ~/$linuxsource/kernel/Makefile ubuntu:~/linux/kernel/
scp ~/$linuxsource/kernel/trace/Makefile ubuntu:~/linux/kernel/trace/
#scp ~/$linuxsource/include/linux/hypercall.h ubuntu:~/linux/include/linux/
scp ~/$linuxsource/kernel/trace/trace.c ubuntu:~/linux/kernel/trace/
scp ~/$linuxsource/kernel/trace/trace.h ubuntu:~/linux/kernel/trace/

scp ~/$linuxsource/include/linux/ftrace.h ubuntu:~/linux/include/linux/ftrace.h
scp ~/$linuxsource/kernel/trace/ftrace.c ubuntu:~/linux/kernel/trace/ftrace.c
scp ~/$linuxsource/init/main.c ubuntu:~/linux/init/main.c
#scp ~/$linuxsource/arch/x86/kernel/head64.c ubuntu:~/linux/arch/x86/kernel/head64.c


ssh ubuntu 'cd linux; make -j$(nproc) && sudo make modules_install && sudo make install;'

#ssh ubuntu 'sudo shutdown now'
#ssh ubuntu 'sudo reboot'