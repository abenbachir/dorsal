
all:
	gcc -o hypercall_guest hypercall-guest.c
	gcc -o hypercall_benchmark hypercall_benchmark.c
	gcc -o hypercount hypercount.c -lm
	gcc -o hypertime hypertime.c
	gcc -o benchmarks benchmarks.c
	scp hypercall_guest hypercall_benchmark vm:~
clean:
	rm hypercall_guest hypercall_benchmark hypercount hypertime


# SRCS   = hypercall-host.c
# OBJS   = $(SRCS:.c=.o)

# obj-m += $(OBJS)


# lttng-tracer-objs += $(shell \
#     if [ $(VERSION) -ge 4 \
#       -o \( $(VERSION) -eq 3 -a $(PATCHLEVEL) -ge 15 -a $(SUBLEVEL) -ge 0 \) ] ; then \
#       echo "lttng-tracepoint.o" ; fi;)

# # EXTRA_CFLAGS += -I/tmp/qemu-install/include

# KERNELDIR ?= /lib/modules/$(shell uname -r)/build

# all:
# 	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules

# clean:
# 	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean
# 	$(RM) Module.markers modules.order
