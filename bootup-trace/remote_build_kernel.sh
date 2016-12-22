#!/usr/bin/env bash

#scp ~/linux/kernel/trace/trace_functions.c ubuntu:~/linux/kernel/trace/
scp ~/linux/kernel/trace/trace_sched_switch.c ubuntu:~/linux/kernel/trace/
scp ~/linux/kernel/trace/trace_functions_graph.c ubuntu:~/linux/kernel/trace/
scp ~/linux/kernel/hypercall.c ubuntu:~/linux/kernel/
scp ~/linux/kernel/Makefile ubuntu:~/linux/kernel/
scp ~/linux/include/linux/hypercall.h ubuntu:~/linux/include/linux/

ssh ubuntu 'cd linux; make -j4; sudo make modules_install; sudo make install;'

ssh ubuntu 'sudo reboot'