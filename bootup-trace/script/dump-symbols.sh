#!/usr/bin/env bash

target=ubuntu2
ssh $target "dmesg > dmsg.txt"
scp $target:~/dmsg.txt ./logs/
ssh $target "sudo cat /proc/kallsyms > kallsyms.map"
scp $target:~/kallsyms.map ./logs/
scp $target:~/linux/System.map ./logs/
ssh $target "ps -eo pid,comm > process.txt"
scp $target:~/process.txt ./logs/
ssh root@$target 'cat /sys/kernel/debug/tracing/trace > /home/abder/bootup-logs.txt'
scp $target:~/bootup-logs.txt ./logs/
echo "ffffffffffffff00 T start_kernel" >> ./logs/symbols.txt
echo "ffffffffffffff01 T ftrace_init" >> ./logs/symbols.txt
echo "ffffffffffffff02 T init_hypergraph_trace" >> ./logs/symbols.txt
echo "ffffffffffffff03 T early_hypergraph_init_trace" >> ./logs/symbols.txt