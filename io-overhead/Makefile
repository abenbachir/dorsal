SRCS   = io_hypertracing.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)
TOP_LTTNG_MODULES_DIR := $(shell dirname $(lastword $(MAKEFILE_LIST)))
ccflags-y += -I$(TOP_LTTNG_MODULES_DIR)

all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules
	# scp io_hypertracing.c ubuntu:~/io_hypertracing/
	# scp Makefile ubuntu:~/io_hypertracing/

clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

