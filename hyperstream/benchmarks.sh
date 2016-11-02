#!/usr/bin/env bash
#set -x

files=(
  "file_1MB.bin"
  "file_10MB.bin"
  "file_100MB.bin"
)

#output="hyperstream.dat"
#echo "size_file,elapsed_time" > $output
for filename in ${files[@]}
do
  size=${filename/trace-/}
  size=${size/.bin/}
  size=${size/.txt/}
  output="./data/hyperstream-${size}.dat"
  echo "elapsed_time" > $output
  sleep 2
  for i in {1..100}
  do
  #  echo "$size," >> $output
    ssh ubuntu "./hyperstream_guest $filename" >> $output
  done
done
