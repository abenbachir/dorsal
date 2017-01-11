SRCS   = my-mod-hypertrace-benchmark.c
OBJS   = $(SRCS:.c=.o)

obj-m += $(OBJS)

EXTRA_CFLAGS += -I/tmp/qemu-install/include

SYMBOL=/tmp/qemu-build/x86_64-softmmu/hypertrace/guest/linux-module/Module.symvers

KBUILD_EXTRA_SYMBOLS=$(SYMBOL)
all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) modules

clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=$(PWD) clean
	$(RM) Module.markers modules.order
