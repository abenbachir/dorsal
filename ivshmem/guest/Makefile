#
# file : Makefile
# desc : Build linux device driver and userspace sources for
#         test with the QEMU ivshmem PCI device
#

usr = ne_ivshmem_shm_guest_usr
bench = ivshmem_benchmark
krn = ne_ivshmem_ldd_basic

ifneq ($(KERNELRELEASE),)

obj-m := $(krn).o

else

KDIR ?= /lib/modules/$$(uname -r)/build

default:
	$(MAKE) -C $(KDIR) M=$$PWD modules
	$(CC) -Wall -Wextra $(CFLAGS) -O2 $(usr).c -o $(usr)
	$(CC) -Wall -Wextra $(CFLAGS) -O2 $(bench).c -o $(bench)

clean:
	$(MAKE) -C $(KDIR) M=$$PWD clean
	rm -f $(usr) $(bench)

.PHONY : clean
endif
