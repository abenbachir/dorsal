#!/usr/bin/env bash

output="./data/parsed-data.csv"

rm -rf $output

for folder in /home/abder/lttng-traces/tracers/syscall/*
do
#        echo ${folder}
    for sub_folder in ${folder}/*
    do
        echo ${sub_folder}
        time ./script/parse-trace.py ${sub_folder} >> $output
#        time ./script/exits-cost.py ${sub_folder} >> ./data/parsed-data-2.csv
#        echo '' >> ./data/parsed-data-2.csv
    done
done


#for folder in /home/abder/lttng-traces/tracers/syscall/perf/*
#do
#    echo ${folder}
#    ./script/exits-cost.py ${folder} >> ./data/test-syscalls.csv
#done
