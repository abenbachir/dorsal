#!/bin/bash
set -x

# LOG_FILE="hypertrace-benchmarks-no_logging.log"
DIRNAME=`pwd`
GUEST_HOSTNAME="abder@ubuntu"
GUEST_NAME="ubuntu"
QEMU_BUILD="$/tmp/qemu-build"
QEMU_INSTALL="/tmp/qemu-install"
QEMU_SOURCE="/home/abder/qemu"


run_benchmarks()
{
  echo "Running benchmarks"	
  LOG_FILE="hypertrace-benchmarks-$1_args.log"
  ssh $GUEST_HOSTNAME "rm ~/$LOG_FILE"
  for i in {0..10}
    do
      ssh $GUEST_HOSTNAME "sudo /home/abder/my-hypertrace-softmmu-benchmark >> $LOG_FILE"
    done
  scp $GUEST_HOSTNAME:~/$LOG_FILE .
}

setup_qemu_with_number_args()
{
	echo "Setup Qemu with $1 args"
	cd $QEMU_BUILD
	# make distclean && rm -rf *-linux-user *-softmm
	$QEMU_SOURCE/configure --enable-trace-backends=ust --with-hypertrace-args=$1 --prefix=$QEMU_INSTALL
	make -j`nproc` 
	make install
	make -C $QEMU_BUILD/x86_64-linux-user/hypertrace/guest/user
    make -C $QEMU_BUILD/x86_64-softmmu/hypertrace/guest/user
    make -C $QEMU_BUILD/x86_64-softmmu/hypertrace/guest/linux-module
	sudo cp $QEMU_INSTALL/bin/* /usr/local/bin/
	cd $DIRNAME # back to the working folder
}

virsh shutdown $GUEST_NAME
sleep 3
setup_qemu_with_number_args 1
# start vm
virsh start $GUEST_NAME
# sleep 6
# run benchmarks
# run_benchmarks 1
