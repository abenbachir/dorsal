
all:
# Compile guest userspace code
#	gcc -o my-hypertrace-user my-hypertrace-benchmark.c \
		/tmp/qemu-build/x86_64-linux-user/hypertrace/guest/user/libqemu-hypertrace-guest.a \
		-I/tmp/qemu-install/include -lpthread
	gcc -o my-hypertrace-softmmu-benchmark my-hypertrace-benchmark.c                              \
       /tmp/qemu-build/x86_64-softmmu/hypertrace/guest/user/libqemu-hypertrace-guest.a \
        -I/tmp/qemu-install/include -lpthread
	# Send to guest
	scp my-hypertrace-softmmu-benchmark ubuntu:~/

clean:
	rm my-hypertrace-softmmu-benchmark
	# rm my-hypertrace-user
