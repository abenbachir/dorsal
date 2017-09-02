SRCS   = cpu_hypertracing_guest.c syscall_hypertracing_guest.c syscall_hypertracing_compress_guest.c sched_hypertracing_compress_guest.c sched_hypertracing_guest.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)
TOP_LTTNG_MODULES_DIR := $(shell dirname $(lastword $(MAKEFILE_LIST)))
ccflags-y += -I$(TOP_LTTNG_MODULES_DIR)

all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules
	gcc -o syscall-micro-benchmark syscall-micro-benchmark.c
	gcc -o sched-switch-micro-benchmark sched-switch-micro-benchmark.c -lpthread


	scp *hypertracing*guest.c vm:~/hypertracing/
	ssh vm 'cd hypertracing; make clean; make'
	# scp Makefile vm:~/hypertracing/
	scp syscall-micro-benchmark sched-switch-micro-benchmark vm:~/
	scp syscall-micro-benchmark sched-switch-micro-benchmark root@vm:~/

	# scp syscall-micro-benchmark vm1:~/
	# scp syscall-micro-benchmark root@vm1:~/

	# ssh vm1 'ssh nested-vm "scp host:~/utils/hypertracing/syscall-micro-benchmark .; sudo cp syscall-micro-benchmark /root/"'

	# ssh vm1 'ssh nested-vm "scp host:~/utils/hypertracing/cpu_hypertracing_guest.c ./hypertracing/"'
	# ssh vm1 'ssh nested-vm "scp host:~/utils/hypertracing/syscall_hypertracing_guest.c ./hypertracing/"'
	# ssh vm1 'ssh nested-vm "scp host:~/utils/hypertracing/syscall_hypertracing_compress_guest.c ./hypertracing/"'

     #ssh vm1 'ssh nested-vm "cd hypertracing; make clean; make"'

    # ssh vm1 'ssh nested-vm "scp host:~/utils/hypertracing/Makefile ./hypertracing/"'


clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

