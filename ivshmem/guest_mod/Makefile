
SRCS   = guest_shm_trace.c guest_pci_device.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)


all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules

clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

.PHONY : clean