
all:
	gcc -o hypercall_sampler hypercall_sampler.c
	gcc -o hypercall_benchmark hypercall_benchmark.c
	scp hypercall_sampler hypercall_benchmark ubuntu:~

clean:
	rm hypercall_sampler hypercall_benchmark
