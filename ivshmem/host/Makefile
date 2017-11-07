usr1 = ne_ivshmem_shm_host_usr
usr2 = ne_ivshmem_send_qeventfd

# gcc -Wall -O2 ne_ivshmem_shm_host_usr.c -o ne_ivshmem_shm_host_usr -lrt


all:
	$(CC) -Wall -O2 $(CFLAGS) -O2 $(usr1).c -o $(usr1) -lrt
	$(CC) -Wall -O2 $(CFLAGS) -O2 $(usr2).c -o $(usr2) -lrt

clean:
	rm -f *.o $(usr1) $(usr2)

.PHONY : clean
