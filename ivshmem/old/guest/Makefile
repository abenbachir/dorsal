#
# file : Makefile
# desc : Build linux device driver and userspace sources for
#         test with the QEMU ivshmem PCI device
#

usr = ne_ivshmem_shm_guest_usr
bench = ivshmem_benchmark
test = ivshmem_test
krn = ne_ivshmem_ldd_basic

ifneq ($(KERNELRELEASE),)

obj-m := $(krn).o

else

KDIR ?= /lib/modules/$$(uname -r)/build

default:
	$(MAKE) -C $(KDIR) M=$$PWD modules
	$(CC) -Wall -Wextra $(CFLAGS) -O2 $(usr).c -o $(usr)
	$(CC) -Wall -Wextra $(CFLAGS) -O2 $(bench).c -o $(bench)
#	$(CC) -Wall -Wextra $(CFLAGS) -O2 $(test).c -o $(test)
	
	scp ivshmem_benchmark abder@VM:/home/abder
clean:
	$(MAKE) -C $(KDIR) M=$$PWD clean
	rm -f $(usr) $(bench) $(test)

.PHONY : clean
endif
