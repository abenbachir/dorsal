#!/usr/bin/env bash
#set -x

output_noins="./data/no-function-graph.dat"
output_ins="./data/function-graph.dat"
output_ins_hypercall="./data/function-graph-dohypercall.dat"
echo "Running benchmarks for : no function graph enabled..."
ssh ubuntu "./simple-program-noins" > $output_noins

echo "Running benchmarks for : function graph enabled..."
ssh ubuntu "./simple-program-ins" > $output_ins

echo "Running benchmarks for : function graph enabled + hypercall ..."
ssh ubuntu "./simple-program-ins-dohypercall" > $output_ins_hypercall
