SRCS   = hypergraph.c simple_proc.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)


all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules
	scp hypergraph.c ubuntu:~/hypergraph/
	scp simple_proc.c ubuntu:~/simple_proc/
clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

