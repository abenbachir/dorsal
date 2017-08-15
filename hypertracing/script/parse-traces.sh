#!/usr/bin/env bash


#for folder in /home/abder/lttng-traces/hypertracing/cpu/*
#do
##        echo ${folder}
#    for sub_folder in ${folder}/*
#    do
#        echo ${sub_folder}
#        ./script/exits-cost.py ${sub_folder} >> ./data/cpu-workload-exits-cost2.csv
#    done
#done


for folder in /home/abder/lttng-traces/hypertracing/cpu/perf/*
do
    echo ${folder}
    ./script/exits-cost.py ${folder} >> ./data/cc-cpu-workload-exits-cost.csv
done
