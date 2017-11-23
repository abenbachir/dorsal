SRCS   = host_shm_vmsync.c mmap.c vm_mmap.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)

# ccflags-y := -DDEBUG -g -std=gnu99 -Werror -Wno-declaration-after-statement -Wframe-larger-than=1000000000

all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules

clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order

.PHONY : clean