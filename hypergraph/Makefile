SRCS   = hypergraph-host.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)


all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules
	scp hypergraph.c ubuntu:~/hypergraph/
	scp hypergraph-host.c ubuntu:/home/abder/hypergraph/

clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

