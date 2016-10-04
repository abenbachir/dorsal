#!/bin/bash
set -x

LOG_FILE="hypertrace-benchmarks.log"
GUEST_HOSTNAME="abder@ubuntu"
hypertrace_args={1}
run_benchmarks()
{
  echo "Running benchmarks"	
  ssh $GUEST_HOSTNAME "rm ~/$LOG_FILE"
  for i in {0..10}
  do
   ssh $GUEST_HOSTNAME "sudo /home/abder/my-hypertrace-softmmu-benchmark >> $LOG_FILE"
  done
  scp $GUEST_HOSTNAME:~/$LOG_FILE .
}


run_benchmarks
