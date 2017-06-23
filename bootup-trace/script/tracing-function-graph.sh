#!/usr/bin/env bash
set -x

sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
sudo echo nop > /sys/kernel/debug/tracing/current_tracer

sudo echo function_graph > /sys/kernel/debug/tracing/current_tracer
sudo echo funcgraph-proc > /sys/kernel/debug/tracing/trace_options
sudo echo nofuncgraph-irqs > /sys/kernel/debug/tracing/trace_options
sudo echo 1 > /sys/kernel/debug/tracing/tracing_on
sleep 0.1
sudo echo 0 > /sys/kernel/debug/tracing/tracing_on

sudo cat /sys/kernel/debug/tracing/trace > ./logs/local-trace.txt