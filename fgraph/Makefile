SRCS   = fgraph.c simple_proc.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)


all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules
	scp fgraph.c ubuntu:~/fgraph/
	scp simple_proc.c ubuntu:~/simple_proc/
clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

