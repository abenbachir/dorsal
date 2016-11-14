#!/usr/bin/env bash
#set -x

output_noins="./data/no-function-graph.dat"
output_ins="./data/function-graph.dat"
output_ins_hypercall="./data/function-graph-dohypercall.dat"
echo "Running benchmarks for : no function graph enabled..."
echo "# Merge sort elapsed time no function graph enabled" > $output_noins
echo "elapsed_time" >> $output_noins
for i in {1..100}
do
	ssh ubuntu "./simple-program-noins" >> $output_noins
done

echo "Running benchmarks for : function graph enabled..."
echo "# Merge sort elapsed time with function graph enabled" > $output_ins
echo "elapsed_time" >> $output_ins
for i in {1..100}
do
	ssh ubuntu "./simple-program-ins" >> $output_ins
done


echo "Running benchmarks for : function graph enabled + hypercall ..."
echo "# Merge sort elapsed time with function graph enabled + hypercall" > $output_ins
echo "elapsed_time" >> $output_ins
for i in {1..100}
do
	ssh ubuntu "./simple-program-ins-dohypercall" >> $output_ins_hypercall
done