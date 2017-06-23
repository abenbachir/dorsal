#!/usr/bin/env bash

ssh ubuntu "dmesg > dmsg.txt"
scp ubuntu:~/dmsg.txt ./logs/
ssh ubuntu "sudo cat /proc/kallsyms > kallsyms.map"
scp ubuntu:~/kallsyms.map ./logs/
scp ubuntu:~/linux/System.map ./logs/
ssh ubuntu "ps -eo pid,comm > process.txt"
scp ubuntu:~/process.txt ./logs/
ssh root@ubuntu 'cat /sys/kernel/debug/tracing/trace > /home/abder/bootup-logs.txt'
scp ubuntu:~/bootup-logs.txt ./logs/
echo "ffffffffffffff00 T start_kernel" >> ./logs/symbols.txt
echo "ffffffffffffff01 T ftrace_init" >> ./logs/symbols.txt
echo "ffffffffffffff02 T init_hypergraph_trace" >> ./logs/symbols.txt
echo "ffffffffffffff03 T early_hypergraph_init_trace" >> ./logs/symbols.txt