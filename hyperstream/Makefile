SRCS   = hyperstream_host.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)
TOP_LTTNG_MODULES_DIR := $(shell dirname $(lastword $(MAKEFILE_LIST)))


all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules
	gcc -o hyperstream_guest hyperstream_guest.c
	scp hyperstream_guest hyperstream_host.ko ubuntu:~

clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order
	rm hyperstream_guest

