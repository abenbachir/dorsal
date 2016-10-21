#!/usr/bin/env bash
#set -x

files=(
  "trace-58MB.txt"
  "trace-116MB.txt"
  "trace-522MB.txt"
)

#output="hyperstream.dat"
#echo "size_file,elapsed_time" > $output
for filename in ${files[@]}
do
  size=${filename/trace-/}
  size=${size/.txt/}
  output="hyperstream-${size}.dat"
  echo "elapsed_time" > $output
  sleep 2
  for i in {1..1000}
  do
  #  echo "$size," >> $output
    ssh ubuntu "./hyperstream_guest $filename" >> $output
  done
done
